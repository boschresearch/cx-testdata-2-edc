from fastapi import APIRouter, Body
from pydantic import BaseModel, Field, constr
from typing import Optional
from uuid import uuid4
import requests
import logging

from notifications_model import QualityNotificationReceiveRequestBody, QualityNotificationReceiveRequestHeader, QualityClassification, QualitySeverity, QualityNotificationReceivePayload
from storage import store

router = APIRouter(tags=['Private'])

class PlainMessageBody(BaseModel):
    recipientBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the receiver. Actually, this value is not used to resolve the quality notification. Rather, it is used to do a plausibility check.',
        example='BPNL00000003BV4H',
    )
    relatedNotificationId: Optional[str] = Field(
        None,
        description='A UUIDv4 to uniquely identify a related quality notification.',
        example='',
    )
    information: Optional[constr(max_length=1000)] = Field(
        None, example='Gear boxes loose oil while driving.'
    )


@router.post('/api/sendplainmessage')
def send_plain_message(body: PlainMessageBody = Body(...)):
    print(body)
    msg_id = str(uuid4())
    msg = QualityNotificationReceiveRequestBody(
        header=QualityNotificationReceiveRequestHeader(
            notificationId=msg_id,
            senderBPN='AAA',
            senderAddress='http://localhost',
            recipientBPN=body.recipientBPN,
            classification=QualityClassification.QM_Investigation,
            severity=QualitySeverity.MINOR,
        ),
        content=QualityNotificationReceivePayload(
            information=body.information,
            listOfAffectedItems=[],
        )
    )
    if body.relatedNotificationId:
        # this is a message as a response. it is part of a 'message thread'
        msg.header.relatedNotificationId = body.relatedNotificationId

    # send the message
    data = msg.dict()
    base_endpoint = lookup_bpn_endpoint(bpn=body.recipientBPN)
    endpoint = f"{base_endpoint}/qualityinvestigations/receive"
    r = requests.post(endpoint, json=data)
    if not r.ok:
        logging.error(f"Could not send message to endpoint: {endpoint}. Reason: {r.reason} Content: {r.content}")
    
    # store the message (for later replies / references)
    store(msg_id=msg_id, msg=msg.dict())
    return { 'notificationId': msg_id }



def lookup_bpn_endpoint(bpn: str):
    if bpn == 'BPNL00000003BV4H':
        return 'http://localhost:8081'


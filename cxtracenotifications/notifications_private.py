import os
from fastapi import APIRouter, Body
from pydantic import BaseModel, Field, constr
from typing import Optional
from uuid import uuid4
import requests
from requests.auth import HTTPBasicAuth
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
    WRAPPER_BASIC_AUTH_USER = os.getenv('WRAPPER_BASIC_AUTH_USER', 'someuser')
    WRAPPER_BASIC_AUTH_PASSWORD = os.getenv('WRAPPER_BASIC_AUTH_PASSWORD', 'somepassword')
    WRAPPER_ENDPOINT_BASE_URL = os.getenv('WRAPPER_ENDPOINT_BASE_URL', '')

    r = None
    url = ''
    if not WRAPPER_ENDPOINT_BASE_URL:
        # (local dev) without EDC
        print("Sending notification in local dev / WITHOUT EDC. Please set WRAPPER_ENDPOINT_BASE_URL if EDC is required!")
        url = f"{base_endpoint}/qualityinvestigations/receive"
        r = requests.post(url, json=data)
    else:
        # probably default case. going via api-wrapper through the EDC
        print(f"Using WRAPPER_BASIC_AUTH_USER: {WRAPPER_BASIC_AUTH_USER} Change via env var")
        print("Using secret WRAPPER_BASIC_AUTH_PASSWORD. Change via env var")
        api_wrapper = WRAPPER_ENDPOINT_BASE_URL
        if not api_wrapper.endswith('/api/service'):
            api_wrapper = api_wrapper + '/api/service'
            print(f"Updated api-wrapper url: {api_wrapper}")
        # bug in api-wrapper. must end with '/submodel' or something else
        url = f"{api_wrapper}/qualityinvestigationnotification-receive/xxx?provider-connector-url={base_endpoint}"
        auth = HTTPBasicAuth(username=WRAPPER_BASIC_AUTH_USER, password=WRAPPER_BASIC_AUTH_PASSWORD)
        r = requests.post(url, auth=auth, json=data)


    if not r.ok:
        logging.error(f"Could not send message to endpoint: {url}. Reason: {r.reason} Content: {r.content}")
    
    print(f"{r.status_code}: {r.content}")
    
    # store the message (for later replies / references)
    store(msg_id=msg_id, msg=msg.dict())
    return { 'notificationId': msg_id }



def lookup_bpn_endpoint(bpn: str):
    if bpn == 'BPNL00000003BV4H':
        return 'http://localhost:8081'
    if bpn == 'BPNL00000003B5MJ':
        return 'http://cxdev.germanywestcentral.cloudapp.azure.com:8185/BPNL00000003B5MJ'


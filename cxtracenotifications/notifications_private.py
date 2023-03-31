import os
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel, Field, constr
from typing import Optional
from uuid import uuid4
import requests
from requests.auth import HTTPBasicAuth
import logging

from settings import QUALITY_INVESTIGATION_NOTIFICATION_ASSET_ID
from notifications_model import QualityNotificationReceiveRequestBody, QualityNotificationReceiveRequestHeader, QualityClassification, QualitySeverity, QualityNotificationReceivePayload
from pycxids.utils.storage import FileStorageEngine
from pycxids.edc.api import EdcConsumer
from pycxids.edc.settings import PROVIDER_EDC_BASE_URL, PROVIDER_EDC_API_KEY, RECEIVER_SERVICE_BASE_URL, IDS_PATH

STORAGE_DIR = os.getenv('STORAGE_DIR', 'notifications')
AGREEMENT_CACHE_FN = os.path.join(STORAGE_DIR, 'agreement_cache.json')
agreement_cache = FileStorageEngine(storage_fn=AGREEMENT_CACHE_FN)

router = APIRouter(tags=['Private'])

class PlainMessageBody(BaseModel):
    recipientBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the receiver. Actually, this value is not used to resolve the quality notification. Rather, it is used to do a plausibility check.',
        example='BPNL00000003B5MJ',
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
    ids_base = lookup_bpn_endpoint(bpn=body.recipientBPN)

    if not ids_base:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not lookup IDS endpoint for given BPN: {body.recipientBPN}")

    consumer = EdcConsumer(
            edc_data_managment_base_url=PROVIDER_EDC_BASE_URL,
            auth_key=PROVIDER_EDC_API_KEY,
            token_receiver_service_base_url=RECEIVER_SERVICE_BASE_URL,
        ) # provider / consumer is no difference here, just relevant how the ENV vars are named. We use 'provider' here...

    ids_endpoint = ids_base
    if not IDS_PATH in ids_endpoint:
        ids_endpoint = f"{ids_base}{IDS_PATH}"
    asset_id = QUALITY_INVESTIGATION_NOTIFICATION_ASSET_ID
    cache_key = f"{ids_endpoint}{asset_id}"
    #agreement_id = agreement_cache.get(cache_key, None)
    agreement_id = None # disable cache for now
    if not agreement_id:
        # negotiate
        agreement_id = consumer.negotiate_contract_and_wait_with_asset(provider_ids_endpoint=ids_endpoint, asset_id=asset_id)
        agreement_cache.put(cache_key, agreement_id)

    provider_edr = consumer.transfer_and_wait_provider_edr(provider_ids_endpoint=ids_endpoint, asset_id=asset_id, agreement_id=agreement_id)

    r = None
    url = ''
    if False:
        # (local dev) without EDC
        print("Sending notification in local dev / WITHOUT EDC. Please set WRAPPER_ENDPOINT_BASE_URL if EDC is required!")
        url = f"{base_endpoint}/qualityinvestigations/receive"
        r = requests.post(url, json=data)
    else:
        # probably default case. going via api-wrapper through the EDC
        url = f"{provider_edr['baseUrl']}"
        r = requests.post(url, json=data, headers={'Authorization': provider_edr['authCode']})


    if not r.ok:
        logging.error(f"Could not send message to endpoint: {url}. Reason: {r.reason} Content: {r.content}")
    
    print(f"{r.status_code}: {r.content}")
    
    # store the message (for later replies / references)
    msg_storage_fn = os.path.join(STORAGE_DIR, msg_id)
    msg_storage = FileStorageEngine(storage_fn=msg_storage_fn)
    msg_storage.put(msg_id, msg.dict())
    return { 'notificationId': msg_id }



def lookup_bpn_endpoint(bpn: str):
    if bpn == 'BPNLconsumer':
        return 'http://consumer-control-plane:8282'
    if bpn == 'BPNLprovider':
        return 'http://provider-control-plane:8282'

    if bpn == 'BPNL00000003BV4H':
        return 'http://localhost:8081'
    if bpn == 'BPNL00000003B5MJ':
        return 'http://cxdev.germanywestcentral.cloudapp.azure.com:8185/BPNL00000003B5MJ'

    return None


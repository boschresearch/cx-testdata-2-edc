import os
import json
import argparse
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from notifications_private import router as notifications_private

from notifications_model import QualityNotificationReceiveRequestBody, QualityNotificationUpdateRequestBody
from storage import store
from notifications_edc_helper import register_endpoints


app = FastAPI(title="Catena-X Traceability Notifications")

# CORS configuration #
origins = [
    "*",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"])

app.include_router(notifications_private)


@app.post('/qualityinvestigations/receive')
def qualityinvestigations_receive(body: QualityNotificationReceiveRequestBody = Body(...)):
    print(body)
    content = json.dumps(body.json(), indent=4)
    #content = body.json()
    print(content)
    msg_id = body.header.notificationId
    ref_id = body.header.relatedNotificationId
    store(msg_id=msg_id, msg=body.json(), reference_id=ref_id)

#@app.post('/update')
def update(body: QualityNotificationUpdateRequestBody = Body(...)):
    pass

#@app.post('resolve')
def resolve():
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--register-endpoints', help='If set, endpoints will be registered as EDC asset.', action='store_true', default=False)

    args = parser.parse_args()
    if args.register_endpoints:
        AUTH_HTTP_HEADER_KEY = os.getenv('AUTH_HTTP_HEADER_KEY', 'X-Api-Key')
        print(f"Using EDC data managment with http header: {AUTH_HTTP_HEADER_KEY}")
        AUTH_HTTP_HEADER_VALUE = os.getenv('AUTH_HTTP_HEADER_VALUE', '')
        assert AUTH_HTTP_HEADER_VALUE, "Please set env"
        print(f"Using EDC data managment with http header: {AUTH_HTTP_HEADER_KEY} and secret key.")
        EDC_DATA_MGMT_ENDPOINT = os.getenv('EDC_DATA_MGMT_ENDPOINT', '')
        assert EDC_DATA_MGMT_ENDPOINT, "Please set env"
        print(f"Using data managment endpoint: {EDC_DATA_MGMT_ENDPOINT}")
        BACKEND_ENDPOINT_BASE_URL = os.getenv('BACKEND_ENDPOINT_BASE_URL', '')
        assert BACKEND_ENDPOINT_BASE_URL, "Please set env"
        print(f"Using public (EDC reachable) backend endpoint base url (this service): {BACKEND_ENDPOINT_BASE_URL}")
        register_endpoints(
            edc_data_management_endpoint=EDC_DATA_MGMT_ENDPOINT,
            backend_endpoint_base_url=BACKEND_ENDPOINT_BASE_URL,
            auth_key=AUTH_HTTP_HEADER_KEY,
            auth_value=AUTH_HTTP_HEADER_VALUE,
        )

    import uvicorn
    port = os.getenv('PORT', '80')
    workers = os.getenv('WORKERS', '5')
    uvicorn.run("notifications:app", host="0.0.0.0", port=int(port), workers=int(workers), reload=False)

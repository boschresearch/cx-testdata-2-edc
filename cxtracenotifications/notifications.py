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
    content = json.dumps(body.dict(), indent=4)
    print(content)
    msg_id = body.header.notificationId
    ref_id = body.header.relatedNotificationId
    store(msg_id=msg_id, msg=body.dict(), reference_id=ref_id)

#@app.post('/update')
def update(body: QualityNotificationUpdateRequestBody = Body(...)):
    pass

#@app.post('resolve')
def resolve():
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--register-endpoints', help='Endpoint Base URL', default=None)

    args = parser.parse_args()
    if args.register_endpoints:
        auth_key = os.getenv('AUTH_KEY', 'X-Api-Key')
        auth_value = os.getenv('AUTH_VALUE', '123456')
        edc_data_mgmt_endpoint = os.getenv('EDC_DATA_MGMT_ENDPOINT', 'http://localhost/data-management/')
        register_endpoints(
            edc_data_management_endpoint=edc_data_mgmt_endpoint,
            backend_endpoint_base_url=args.register_endpoints,
            auth_key=auth_key,
            auth_value=auth_value,
        )
        os._exit()

    import uvicorn
    port = os.getenv('PORT', '80')
    workers = os.getenv('WORKERS', '5')
    uvicorn.run("notifications:app", host="0.0.0.0", port=int(port), workers=int(workers), reload=False)

import os
import json
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from notifications_private import router as notifications_private

from notifications_model import QualityNotificationReceiveRequestBody, QualityNotificationUpdateRequestBody

app = FastAPI(title="Catena-X Traceability Notifications")

# CORS configuration #
origins = [
    "*",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"])

app.include_router(notifications_private)


@app.post('/receive')
def receive(body: QualityNotificationReceiveRequestBody = Body(...)):
    print(body)
    print(json.dumps(body, indent=4))

@app.post('/update')
def update(body: QualityNotificationUpdateRequestBody = Body(...)):
    pass

@app.post('resolve')
def resolve():
    pass

if __name__ == '__main__':
    import uvicorn
    port = os.getenv('PORT', '80')
    workers = os.getenv('WORKERS', '5')
    uvicorn.run("notifications:app", host="0.0.0.0", port=int(port), workers=int(workers), reload=False)

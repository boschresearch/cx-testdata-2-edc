import registry_handling as reg
import edc_handling as edc

from fastapi import FastAPI, Body, Security, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import json
import os

app = FastAPI(title='Traceability Case Study Backend')

origins = [
    '*'
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['*'], allow_headers=['*'])


API_KEY_NAME = 'X-Api-Key'
API_KEY = os.getenv('API_KEY', '1234')
security_api_key = APIKeyHeader(name=API_KEY_NAME, auto_error=True) #auto_error only check if key exists!

def check_api_key(api_key: str = Security(security_api_key)):
    if not api_key == API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Wrong {API_KEY_NAME} value.")


@app.post('/', dependencies=[Security(check_api_key)])
def post(body: dict = Body(...)):
    print(json.dumps(body, indent=4))


if __name__ == '__main__':
    import uvicorn
    port = os.getenv('PORT', '8080')
    workers = os.getenv('WORKERS', '3')
    uvicorn.run("case-study:app", host="0.0.0.0", port=int(port), workers=int(workers), reload=False)

import registry_handling as reg
import edc_handling as edc

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

app = FastAPI(title='Traceability Case Study Backend')

origins = [
    '*'
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['*'])


@app.post('/')
def post(body: dict = Body(...)):
    print(json.dumps(body, indent=4))


if __name__ == '__main__':
    import uvicorn
    port = os.getenv('PORT', '8080')
    workers = os.getenv('WORKERS', '3')
    uvicorn.run("case-study:app", host="0.0.0.0", port=int(port), workers=int(workers), reload=False)

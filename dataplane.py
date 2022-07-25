# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/catenax-ng/product-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

from email import header
from email.policy import default
import os
from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import jwt
from datetime import datetime


PUB_KEY_PROVIDER_CP = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA10xqGDVWgfEwKhJQwKr7
ZdovXfEMHOixhVPIzVw2/IR7Ud/q83FfJ/++iLwXtsAHY6R6UxhESZDt2RkN965L
WGFKg09w1ZJ5NPPARYQt+1lL24yEuJLK2clQUnNYTD9M0aOL4cY7VWXGwnPTWa1U
xosJWzcJPwHqo7rMPt+x0sCOMIm+75KbUdp6uiol8WXvm8h179xu8KywN/XEmor4
k1bNlafuUmg1zHXfTp/V1Oga3Ze/5mTe0qjE72c7RVqB52j8LO3am59dnio1asoO
J4OD3shNsgA1xJRLbhc97EmBwk4XE2xJjbfUcUAcauBetLdRHp1hJp64LQEphZTc
RwIDAQAB
-----END PUBLIC KEY-----
"""

app = FastAPI(title="Dataplane Python Implementation")


origins = [
    "*",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"])

@app.get('/{path:path}')
async def get_default(path: str, request: Request, authorization = Header(default=None)):
    """
    validation_url = 'http://cxdev.germanywestcentral.cloudapp.azure.com:8184/validation/token'
    headers = {
        'Authorization': authorization
    }
    r = requests.get(validation_url, headers=headers)

    j = r.json()
    print('ControlPlane:')
    print(json.dumps(j, indent=4))
    """
    
    try:
        options = {
            'verify_signature' : True,
            'require' : ["exp"],
            'verify_exp': True, # check that exp (expiration) claim value is in the future
        }
        dec = jwt.decode(authorization, PUB_KEY_PROVIDER_CP, algorithms=["RS256"], options=options)
        print('Self Decoded:')
        print(json.dumps(dec, indent=4))
        exp = datetime.fromtimestamp(dec['exp'])
        print(f"exp for humans UTC: {exp.isoformat()}")

        #data = json.loads(j['claims']['dad'])
        data = json.loads(dec['dad'])
        endpoint = data['properties']['endpoint']
        print(endpoint)

        r = requests.get(endpoint)
        j = r.json()

        return j

    except Exception as ex:
        print(ex)
        raise ex

    return {}

if __name__ == '__main__':
    import uvicorn
    port = os.getenv('PORT', '6060')
    uvicorn.run("dataplane:app", host="0.0.0.0", port=int(port), reload=True)

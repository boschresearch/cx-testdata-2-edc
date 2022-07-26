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

PUB_KEY_CONSUMER_CP = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8F7/ik/vWbxDS9yQHMqm
I22zbWdmLgKTKz6pWK2lo25rhia+rsYchIcvwol6qzS42BtDeASbBMz1hcJP2pBt
zAGNFqtrrslKzJDVHAA+0WIuCS7ea62QN3E+uwxNt0oawQ44h6E3E49Kzpk+F8AY
ycHuoG+XhaubxX4FXEUtM4cw8Bc3c0z2jnO9qVGXj7sRNeK7UniJxg/VxSavzyx5
ZNCq0uYjyPu7CcBW4TssTgRR7CITmEr+2iDlsVXolRny8/Co9sT1fsNBfGgomPVr
2HEsTgnnIhlUgPkZ2G/W4cbKLPWxzyWVCrdtFlWNARQlEydHihWkWMX1a+SN+IxS
ewIDAQAB
-----END PUBLIC KEY-----
"""

app = FastAPI(title="Dataplane Python Implementation")


origins = [
    "*",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"])

@app.get('/consumer/{path:path}')
async def get_default(path: str, request: Request, authorization = Header(default=None)):
    try:
        dec = decode(token=authorization, pub_key=PUB_KEY_CONSUMER_CP)
        print(json.dumps(dec, indent=4))
        dad = json.loads(dec['dad'])
        headers = {
            dad['properties']['authKey']: dad['properties']['authCode']
        }
        url = f"{dad['properties']['endpoint']}{path}"
        r = requests.get(url, headers=headers)
        if not r.ok:
            print(r.content)
        j = r.json()
        return j
    except Exception as ex:
        print(ex)
        raise ex

    return {}

def decode(token: str, pub_key: str):
    options = {
        'verify_signature' : True,
        'require' : ["exp"],
        'verify_exp': True, # check that exp (expiration) claim value is in the future
    }
    dec = jwt.decode(token, pub_key, algorithms=["RS256"], options=options)
    return dec


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
        dec = decode(token=authorization, pub_key=PUB_KEY_PROVIDER_CP)
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
    uvicorn.run("dataplane:app", host="0.0.0.0", port=int(port), workers=2, reload=False)

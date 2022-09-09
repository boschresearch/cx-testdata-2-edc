# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/catenax-ng/product-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

import inspect
import os
import shelve
from fastapi import FastAPI, HTTPException, Query, Security, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from dependencies import settings, DB_CX_ITEMS, ASSEMBLY_PART_RELATIONSHIP_PATH, SCHEMA_ASSEMBLY_PART_RELATIONSHIP_LOOKUP_STRING, SCHEMA_MATERIAL_FOR_RECYCLING_LOOKUP_STRING, SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING, SERIAL_PART_TYPIZATION_ENDPOINT_PATH, MATERIAL_FOR_RECYCLING_PATH, get_first_match


app = FastAPI(title="CX Testdata Submodel Endpoint Server for R1")

# CORS configuration #
origins = [
    "*",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"])

# SECURITY - API Key configuration #
API_KEY_NAME = settings.endpoint_base_url_internal_auth_key
API_KEY = settings.endpoint_base_url_internal_auth_code

# TODO: how to disable it in a configurable way?
security_api_key = APIKeyHeader(name=API_KEY_NAME, auto_error=False) #auto_error only check if key exists!

def check_api_key(api_key: str = Security(security_api_key)):
    if not api_key == API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Wrong {API_KEY_NAME} value.")



def get_item(catenaXId:str):
    with shelve.open(DB_CX_ITEMS, 'r') as db:
        item = db[catenaXId]
        return item

def get_sm_for_item(item, schema: str):
    return get_first_match(item=item, key_match=schema, default_return=None)

def check_params(content: str, extent: str):
    if content != 'value':
        raise HTTPException(status_code=501, detail="Parameter 'content' MUST be 'value'.")
    if extent != 'withBlobValue':
        raise HTTPException(status_code=501, detail="Parameter 'extent' MUST be 'withBlobValue'.")

@app.get(SERIAL_PART_TYPIZATION_ENDPOINT_PATH + '/{catenaXId}', dependencies=[Security(check_api_key)])
async def get_serial_part_typization(catenaXId: str, content: str = Query(example='value', default=None), extent: str = Query(example='withBlobValue', default=None)):
    print(f"get_serial_part_typization catenaXId: {catenaXId}")
    #check_params(content=content, extent=extent)
    try:
        item = get_item(catenaXId=catenaXId)
        sm_data = get_sm_for_item(item, schema=SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING)[0]
        print(sm_data)
        return sm_data
    except Exception:
        return {}

@app.get(ASSEMBLY_PART_RELATIONSHIP_PATH + '/{catenaXId}', dependencies=[Security(check_api_key)])
async def get_assembly_part_relationship(catenaXId: str, content: str = Query(example='value', default=None), extent: str = Query(example='withBlobValue', default=None)):
    print(f"get_assembly_part_relationship catenaXId: {catenaXId}")
    #check_params(content=content, extent=extent)
    try:
        item = get_item(catenaXId=catenaXId)
        sm_data = get_sm_for_item(item, schema=SCHEMA_ASSEMBLY_PART_RELATIONSHIP_LOOKUP_STRING)[0]
        return sm_data
    except Exception:
        return {}

@app.get(MATERIAL_FOR_RECYCLING_PATH + '/{catenaXId}', dependencies=[Security(check_api_key)])
async def get_material_for_recycling(catenaXId: str, content: str = Query(example='value', default=None), extent: str = Query(example='withBlobValue', default=None)):
    print(f"get_material_for_recycling catenaXId: {catenaXId}")
    #check_params(content=content, extent=extent)
    try:
        item = get_item(catenaXId=catenaXId)
        sm_data = get_sm_for_item(item, schema=SCHEMA_MATERIAL_FOR_RECYCLING_LOOKUP_STRING)[0]
        return sm_data
    except Exception:
        return {}

#@app.on_event('startup')
def server_startup():
    print('server_startup()')
    with shelve.open(DB_CX_ITEMS, 'c') as db: # c to create if doesn't exist
        keys = list(db.keys())
        print(keys)


if __name__ == '__main__':
    server_startup() # only run once, not for every worker
    import uvicorn
    port = os.getenv('PORT', '8080')
    host = os.getenv('HOST', "0.0.0.0")
    workers = os.getenv('WORKERS', '3')
    uvicorn.run("main:app", host=host, port=int(port), workers=int(workers), reload=False)

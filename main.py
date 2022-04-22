# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/catenax-ng/product-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

import os
import shelve
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dependencies import DB_CX_ITEMS, ASSEMBLY_PART_RELATIONSHIP_PATH, SCHEMA_ASSEMBLY_PART_RELATIONSHIP_PREFIX, SCHEMA_MATERIAL_FOR_RECYCLING_PREFIX, SERIAL_PART_TYPIZATION_ENDPOINT_PATH, MATERIAL_FOR_RECYCLING_PATH, SCHEMA_SERIAL_PART_TYPIZATION_PREFIX


app = FastAPI(title="CX Testdata Submodel Endpoint Server for R1")



origins = [
    "*",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"])

def get_item(catenaXId:str):
    with shelve.open(DB_CX_ITEMS, 'r') as db:
        item = db[catenaXId]
        return item

def get_sm_for_item(item, schema: str):
    for key in item.keys():
        if key.startswith(schema):
            return item[key]
    return None

@app.get(SERIAL_PART_TYPIZATION_ENDPOINT_PATH + '/{catenaXId}')
async def get_serial_part_typization(catenaXId: str):
    try:
        item = get_item(catenaXId=catenaXId)
        sm_data = get_sm_for_item(item, schema=SCHEMA_SERIAL_PART_TYPIZATION_PREFIX)
        return sm_data
    except Exception:
        return {}

@app.get(ASSEMBLY_PART_RELATIONSHIP_PATH + '/{catenaXId}')
async def get_assembly_part_relationship(catenaXId: str):
    try:
        item = get_item(catenaXId=catenaXId)
        sm_data = get_sm_for_item(item, schema=SCHEMA_ASSEMBLY_PART_RELATIONSHIP_PREFIX)
        return sm_data
    except Exception:
        return {}

@app.get(MATERIAL_FOR_RECYCLING_PATH + '/{catenaXId}')
async def get_material_for_recycling(catenaXId: str):
    try:
        item = get_item(catenaXId=catenaXId)
        sm_data = get_sm_for_item(item, schema=SCHEMA_MATERIAL_FOR_RECYCLING_PREFIX)
        return sm_data
    except Exception:
        return {}

@app.on_event('startup')
def server_startup():
    with shelve.open(DB_CX_ITEMS, 'r') as db:
        keys = list(db.keys())
        print(keys)


if __name__ == '__main__':
    import uvicorn
    port = os.getenv('PORT', '8080')
    workers = os.getenv('WORKERS', '5')
    uvicorn.run("main:app", host="0.0.0.0", port=int(port), workers=int(workers), reload=False)

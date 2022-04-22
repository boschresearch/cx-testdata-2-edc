# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/catenax-ng/product-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

import os
import shelve
from uuid import uuid4

REGISTRY_BASE_URL = os.getenv('REGISTRY_BASE_URL', 'http://registry:4243')
EDC_BASE_URL = os.getenv('EDC_BASE_URL', 'http://provider-control-plane:9191/api')
SCHEMA_SERIAL_PART_TYPIZATION = 'https://catenax.com/schema/SerialPartTypization/1.0.0'

SCHEMA_ASSEMBLY_PART_RELATIONSHIP_PREFIX = 'https://catenax.com/schema/AssemblyPartRelationship/'
SCHEMA_SERIAL_PART_TYPIZATION_PREFIX = 'https://catenax.com/schema/SerialPartTypization/'
SCHEMA_MATERIAL_FOR_RECYCLING_PREFIX = 'https://catenax.com/schema/MaterialForRecycling/'

CX_SCHEMA_PREFIX = 'https://catenax.com/schema/'

SERIAL_PART_TYPIZATION_ENDPOINT_PATH = '/serialparttypization'
ASSEMBLY_PART_RELATIONSHIP_PATH = '/assemblypartrelationship'
MATERIAL_FOR_RECYCLING_PATH = '/materialforrecycling'

DB_CX_ITEMS = os.getenv('DB_CX_ITEMS', 'CxItems.db')
DB_EDC_ASSETS = os.getenv('DB_EDC_ASSETS', 'EdcAssets.db')
DB_ID_MAPPINGS = os.getenv('DB_ID_MAPPINGS', 'IdMappings.db')
DB_POLICY_ID_MAPPINGS = os.getenv('DB_POLICY_ID_MAPPINGS', 'PolicyIdMappings.db')

def path_for_schema(schema: str):
    if schema.startswith(SCHEMA_SERIAL_PART_TYPIZATION_PREFIX):
        return SERIAL_PART_TYPIZATION_ENDPOINT_PATH
    if schema.startswith(SCHEMA_ASSEMBLY_PART_RELATIONSHIP_PREFIX):
        return ASSEMBLY_PART_RELATIONSHIP_PATH
    if schema.startswith(SCHEMA_MATERIAL_FOR_RECYCLING_PREFIX):
        return MATERIAL_FOR_RECYCLING_PATH
    return None

def idshort_for_schema(schema: str):
    if schema.startswith(SCHEMA_SERIAL_PART_TYPIZATION_PREFIX):
        return 'SerialPartTypization'
    if schema.startswith(SCHEMA_ASSEMBLY_PART_RELATIONSHIP_PREFIX):
        return 'AssemblyPartRelationship'
    if schema.startswith(SCHEMA_MATERIAL_FOR_RECYCLING_PREFIX):
        return 'MaterialForRecycling'
    return None


def unique_id():
    return 'urn:uuid:' + str(uuid4())

def get_db_item(key: str, dbname: str = DB_CX_ITEMS):
    try:
        with shelve.open(dbname, 'r') as db:
            return db[key]
    except:
        pass
    return None

def get_db_keys(dbname: str = DB_CX_ITEMS):
    try:
        with shelve.open(dbname, 'r') as db:
            return list(db)
    except:
        pass
    return []

def delete_db_item(key: str, dbname = DB_CX_ITEMS):
    """
    Delete item from db.
    False in case of an error (also non existing item) otherwise True
    """
    try:
        with shelve.open(dbname) as db:
            del db[key]
    except:
        return False
    return True

def delete_db_all(dbname: str = DB_CX_ITEMS):
    keys = get_db_keys()
    for key in keys:
        delete_db_item(key=key, dbname=dbname)

def iterate_cx_items_schemas():
    """
    Iterator / yield function to iterate over the cx items.
    Don't repeat the boilerplate code in indivudual create/delete functions
    """
    keys = get_db_keys()
    for key in keys:
        item = get_db_item(key=key)
        cx_id = item.get('catenaXId', '')
        for item_key in item.keys():
            if item_key.startswith(CX_SCHEMA_PREFIX):
                yield {
                    "cx_id": cx_id,
                    "schema": item_key
                }

def iterate_cx_items():
    """
    Iterator / yield function to iterate over the cx items.
    Don't repeat the boilerplate code in indivudual create/delete functions
    """
    keys = get_db_keys()
    for key in keys:
        item = get_db_item(key=key)
        yield item

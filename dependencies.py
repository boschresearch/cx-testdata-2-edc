# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/catenax-ng/product-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

import os
import shelve
from uuid import uuid4
from pydantic import BaseSettings


class Settings(BaseSettings):
    # typically external
    provider_control_plane_base_url: str = 'http://provider-control-plane:8181'
    # used for EDC -> endpoint communication
    endpoint_base_url_internal: str = 'http://localhost:8080'
    # if given add direct (non-EDC) endpoint for it
    endpoint_base_url_external: str = ''
    registry_base_url: str = 'http://registry:4243'
    consumer_aas_proxy_base_url: str = 'http://consumer-aas-proxy-service:4245'
    edc_base_url: str = 'http://provider-control-plane:9191/api'
    edc_api_key: str = ''
    # oauth
    client_id_registry: str = ''
    client_secret_registry: str = ''
    token_url_registry: str = ''

    class Config:
        env_file = os.getenv('ENV_FILE', '.env') # if ENV_FILE is not set, we read env vars from .env by default

settings: Settings = Settings()
# print the settings that we actually use, but leave out the secret field
s_str = settings.json(exclude={'client_secret_registry'}, indent=4)
print('settings:')
print(s_str)

PROVIDER_CONTROL_PLANE_BASE_URL = settings.provider_control_plane_base_url
ENDPOINT_BASE_URL_INTERNAL = settings.endpoint_base_url_internal
ENDPOINT_BASE_URL_EXTERNAL = settings.endpoint_base_url_external

REGISTRY_BASE_URL = settings.registry_base_url
EDC_BASE_URL = settings.edc_base_url
EDC_API_KEY = settings.edc_api_key

CLIENT_ID_REGISTRY = settings.client_id_registry
CLIENT_SECRET_REGISTRY = settings.client_secret_registry
TOKEN_URL_REGISTRY = settings.token_url_registry


SCHEMA_ASSEMBLY_PART_RELATIONSHIP_LOOKUP_STRING = '/schema/AssemblyPartRelationship/'
SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING = '/schema/SerialPartTypization/'
SCHEMA_MATERIAL_FOR_RECYCLING_LOOKUP_STRING = '/schema/MaterialForRecycling/'
SCHEMA_TESTDATA_CONTAINER_LOOKUP_STRING = '/schema/TestDataContainer/'

CX_SCHEMA_LOOKUP_STRING = '/schema/'

SERIAL_PART_TYPIZATION_ENDPOINT_PATH = '/serialparttypization'
ASSEMBLY_PART_RELATIONSHIP_PATH = '/assemblypartrelationship'
MATERIAL_FOR_RECYCLING_PATH = '/materialforrecycling'

DB_CX_ITEMS = os.getenv('DB_CX_ITEMS', 'CxItems.db')
DB_EDC_ASSETS = os.getenv('DB_EDC_ASSETS', 'EdcAssets.db')
DB_ID_MAPPINGS = os.getenv('DB_ID_MAPPINGS', 'IdMappings.db')
DB_POLICY_ID_MAPPINGS = os.getenv('DB_POLICY_ID_MAPPINGS', 'PolicyIdMappings.db')

def path_for_schema(schema: str):
    if SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING in schema:
        return SERIAL_PART_TYPIZATION_ENDPOINT_PATH
    if SCHEMA_ASSEMBLY_PART_RELATIONSHIP_LOOKUP_STRING in schema:
        return ASSEMBLY_PART_RELATIONSHIP_PATH
    if SCHEMA_MATERIAL_FOR_RECYCLING_LOOKUP_STRING in schema:
        return MATERIAL_FOR_RECYCLING_PATH
    return None

def idshort_for_schema(schema: str):
    if SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING in schema:
        return 'SerialPartTypization'
    if SCHEMA_ASSEMBLY_PART_RELATIONSHIP_LOOKUP_STRING in schema:
        return 'AssemblyPartRelationship'
    if SCHEMA_MATERIAL_FOR_RECYCLING_LOOKUP_STRING in schema:
        return 'MaterialForRecycling'
    return None

def get_first_match(item, key_match: str, default_return = None):
    """
    Since the schemas have changed, this is a workaround to work with
    http://catenax.com/schema/
    AND
    http://catenax.io/schema/

    """
    for key in list(item.keys()):
        if key_match in key:
            return item[key]
    return default_return

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
    keys = get_db_keys(dbname=dbname)
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
            if CX_SCHEMA_LOOKUP_STRING in item_key:
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

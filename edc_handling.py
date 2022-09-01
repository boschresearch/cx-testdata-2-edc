# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/catenax-ng/product-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

import shelve
from uuid import uuid4
import requests
import json
import logging
from aas.registry.models.asset_administration_shell_descriptor import AssetAdministrationShellDescriptor
from dependencies import ASSEMBLY_PART_RELATIONSHIP_PATH, BACKWARD_COMPATIBILITY_0_0_6, DB_POLICY_ID_MAPPINGS, EDC_BASE_URL, ENDPOINT_BASE_URL_INTERNAL, MATERIAL_FOR_RECYCLING_PATH, DB_EDC_ASSETS, DB_CX_ITEMS, DB_ID_MAPPINGS, SERIAL_PART_TYPIZATION_ENDPOINT_PATH, get_db_item, iterate_cx_items_schemas, path_for_schema, EDC_API_KEY, settings


def prepare_edc_headers():
    headers = {}
    if EDC_API_KEY:
        headers['X-Api-Key'] = EDC_API_KEY

    return headers

def prepare_aas_id_key_local(cx_id: str):
    """
    A single place to generate the key that we use for the mapping of IDs in our database.
    Just needs to be "unique" in the DB
    """
    return f"AAS_ID-{cx_id}"

def prepare_submodel_id_local(cx_id:str, schema:str):
    """
    That's how we locally map IDs in our database.
    We assume that only 1 aspect / submodel per CX item exists.
    Therefore the schema of it is "enough" uniqueness.
    """
    return f"{cx_id}{schema}"

def prepare_asset_id(cx_id:str, submodel_id:str):
    """
    That's how we currently build asset IDs in Cx
    """
    aas_id = upsert_aas_id(cx_id=cx_id)
    return f"{aas_id}-{submodel_id}"

def upsert_sm_id(cx_id:str, schema:str):
    """
    Create a uuid for the built together "local" unique id.
    Return existing or new uuid
    """
    sm_id_local = prepare_submodel_id_local(cx_id=cx_id, schema=schema)
    sm_id = get_db_item(sm_id_local, dbname=DB_ID_MAPPINGS)
    
    if not sm_id:
        with shelve.open(DB_ID_MAPPINGS) as db:
            new_sm_id = "urn:uuid:" + str(uuid4())
            db[sm_id_local] = new_sm_id
            return new_sm_id

    return sm_id

def upsert_aas_id(cx_id: str):
    """
    Create a uuid for the built together "local" unique id.
    Return existing or new uuid
    """
    key = prepare_aas_id_key_local(cx_id=cx_id)
    aas_id = get_db_item(key=key, dbname=DB_ID_MAPPINGS)
    
    if not aas_id:
        with shelve.open(DB_ID_MAPPINGS) as db:
            new_aas_id = "urn:uuid:" + str(uuid4())
            db[key] = new_aas_id
            return new_aas_id

    return aas_id

def get_asset(asset_id: str):
    r = requests.get(f"{EDC_BASE_URL}/assets/{asset_id}", headers=prepare_edc_headers())
    if r.ok:
        try:
            return r.json()
        except:
            # in provider-control-plane version 0.0.1 it seems the return is successful, but with no content
            # in case there is no asset. catenax-at-home/getting-started-guide version.
            pass
    return None

def create_asset(cx_id: str, asset_id: str, schema: str):
    """
    Create the asset in the EDC.
    Returns the asset information that we used to create it, because EDC itself would not return this.
    EDC only returns the asset_id
    """
    path = path_for_schema(schema=schema)
    if not path:
        raise Exception(f"We can't find a path for the given schema {schema}")

    data = {
        "asset": {
            "properties": {
                "asset:prop:id": asset_id,
                "asset:prop:contenttype": "application/json",
                "asset:prop:policy-id": "use-eu",
            }
        },
        "dataAddress": {
            "properties": {
                "type": "HttpData",
                "endpoint": ENDPOINT_BASE_URL_INTERNAL + path + "/" + cx_id
            }
        }
    }
    r = requests.post(f"{EDC_BASE_URL}/assets", json=data, headers=prepare_edc_headers())
    if not r.ok:
        logging.error(f"Could not create EDC asset. Reason: {r.reason} Content: {r.content}")
        return None
    logging.info(f"EDC asset created for cx_id: {cx_id} asset_id: {asset_id}")
    return data    


def upsert_asset(cx_id:str, schema:str):
    """
    We consider cx_id and schema together are unique. That means, it is NOT allowed to have multiple items for 1 schema (currently a list)
    """
    sm_id = upsert_sm_id(cx_id=cx_id, schema=schema)
    asset_id = prepare_asset_id(cx_id=cx_id, submodel_id=sm_id)

    existing_asset_id = get_asset(asset_id=asset_id)
    if existing_asset_id:
        logging.info(f"EDC asset already exists for cx_id: {cx_id} asset_id: {asset_id}")
        # and don't forget the policy
        upsert_policy(asset_id=asset_id)

        return existing_asset_id

    # or we create a new one in EDC
    asset = create_asset(cx_id=cx_id, asset_id=asset_id, schema=schema)
    # and don't forget the policy
    upsert_policy(asset_id=asset_id)

    return asset_id

def upsert_policy(asset_id: str):
    policy_id = get_db_item(asset_id, DB_POLICY_ID_MAPPINGS)
    if policy_id:
        upsert_contract_definition(policy_id=policy_id)
        return policy_id

    new_policy_id = str(uuid4())

    data = {
        "uid": new_policy_id,
        "policy": {
            "permissions": [
                {
                    "target": asset_id,
                    "action": {
                        "type": "USE"
                    },
                    "edctype": "dataspaceconnector:permission"
                }
            ],
        },
        "@type": {
            "@policytype": "set"
        }
    }

    if settings.backward_compatibility == BACKWARD_COMPATIBILITY_0_0_6:
        # some legacy format if required...
        data = {
            "uid": new_policy_id,
            "permissions": [
                {
                    "target": asset_id,
                    "action": {
                        "type": "USE"
                    },
                    "edctype": "dataspaceconnector:permission"
                }
            ],
            "@type": {
                "@policytype": "set"
            }
        }
    policy_endpoint_path = '/policydefinitions'
    if settings.backward_compatibility == BACKWARD_COMPATIBILITY_0_0_6:
        # legacy endpoint if required...
        policy_endpoint_path = '/policies'

    r = requests.post(f"{EDC_BASE_URL}{policy_endpoint_path}", json=data, headers=prepare_edc_headers())
    if not r.ok:
        logging.error(f"Could not create policy. Reason: {r.reason} Content: {r.content}")
        return None
    with shelve.open(DB_POLICY_ID_MAPPINGS) as db:
        db[asset_id] = new_policy_id
    upsert_contract_definition(policy_id=new_policy_id)
    return new_policy_id

def upsert_contract_definition(policy_id: str):
    # TODO: check if already exists...
    new_id = str(uuid4())
    data = {
        "id": new_id,
        "accessPolicyId": policy_id,
        "contractPolicyId": policy_id,
        "criteria": [],
    }
    r = requests.post(f"{EDC_BASE_URL}/contractdefinitions", json=data, headers=prepare_edc_headers())
    if not r.ok:
        logging.error(f"Could not create Contractdefinition. Continuing. Reason: {r.reason} Content: {r.content}")
    return new_id



def upsert_assets_from_cx_items():
    """
    Loop through the list of local ID mappings and create an EDC asset if it does not exist yet.
    """
    for item in iterate_cx_items_schemas():
        upsert_asset(cx_id=item['cx_id'], schema=item['schema'])

def delete_assets_from_cx_items():
    """
    Deletes all items from EDC. Means: assets, TODO: policy and contractdefinitions
    """
    for item in iterate_cx_items_schemas():
        delete_asset(cx_id=item['cx_id'], schema=item['schema'])

def delete_asset(cx_id: str, schema: str):
    sm_id_local = prepare_submodel_id_local(cx_id=cx_id, schema=schema)
    sm_id = get_db_item(sm_id_local, dbname=DB_ID_MAPPINGS)
    asset_id = prepare_asset_id(cx_id=cx_id, submodel_id=sm_id)

    r = requests.delete(f"{EDC_BASE_URL}/assets/{asset_id}", headers=prepare_edc_headers())
    if not r.ok:
        logging.info(f"Could not delete EDC asset with id: {asset_id}")
        return False
    return True

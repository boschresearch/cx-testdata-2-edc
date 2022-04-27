# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/catenax-ng/product-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

import sys
import os
import json
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from aas.registry.models.asset_administration_shell_descriptor import AssetAdministrationShellDescriptor
from aas.registry.models.identifier_key_value_pair import IdentifierKeyValuePair
from aas.registry.models.submodel_descriptor import SubmodelDescriptor
from aas.registry.models.protocol_information import ProtocolInformation
from aas.registry.models.endpoint import Endpoint
from aas.registry.models.reference import Reference
from dependencies import CLIENT_ID_REGISTRY, CLIENT_SECRET_REGISTRY, CX_SCHEMA_LOOKUP_STRING, DB_CX_ITEMS, ENDPOINT_BASE_URL_EXTERNAL, PROVIDER_CONTROL_PLANE_BASE_URL, SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING, TOKEN_URL_REGISTRY, get_db_item, get_first_match, idshort_for_schema, iterate_cx_items, path_for_schema, REGISTRY_BASE_URL
from edc_handling import upsert_aas_id, upsert_sm_id


session = None

def get_requests_session():
    global session #
    if session:
        return session

    if CLIENT_ID_REGISTRY and CLIENT_SECRET_REGISTRY:
        # https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow
        client = BackendApplicationClient(client_id=CLIENT_ID_REGISTRY)
        s = OAuth2Session(client=client)
        token = s.fetch_token(token_url=TOKEN_URL_REGISTRY, client_secret=CLIENT_SECRET_REGISTRY)
        # TODO: have a look at expires_at and check with refresh token
        session = OAuth2Session(client_id=CLIENT_ID_REGISTRY, token=token)
    else:
        session = requests.Session()
    
    return session

def lookup_by_globalAssetId(globalAssetId: str):
    """
    Find a AAS by the globalAssetId
    Everying else than 1 exact match returns None (for now)
    """
    query1 = [{
            'key': 'globalAssetId',
            'value': globalAssetId,
        }]
    query1_str = json.dumps(query1)
    query = {
        'assetIds': query1_str
    }
    r = get_requests_session().get(f"{REGISTRY_BASE_URL}/lookup/shells", params=query)
    if not r.ok:
        return None
    aas_ids = r.json()
    if len(aas_ids) != 1:
        return None
    return aas_ids[0]

def prepare_edc_submodel_endpoint_address(aas_id: str, sm_id: str, bpn: str):
    """
    # {{providerControlPlaneDockerInternal}}/{{providerBpn}}/{{digitalTwinId}}-{{digitalTwinSubmodelId}}
    """
    return f"{PROVIDER_CONTROL_PLANE_BASE_URL}/{bpn}/{aas_id}-{sm_id}/submodel?content=value&extent=withBlobValue"

def prepare_submodel_descriptor( cx_id: str, schema: str, aas_id: str, bpn: str):
    """
    Prepares a Submodel
    """
    path = path_for_schema(schema=schema)
    sm_id = upsert_sm_id(cx_id=cx_id, schema=schema)
    edc_endpoint = prepare_edc_submodel_endpoint_address(aas_id=aas_id, sm_id=sm_id, bpn=bpn)
    endpoints = [
        Endpoint(
            interface='SUBMODEL-1.0RC02', #TODO: why RC02?
            protocol_information=ProtocolInformation(
                endpoint_address=edc_endpoint,
                endpointProtocol="IDS/ECLIPSE DATASPACE CONNECTOR",
                endpointProtocolVersion="0.0.1-SNAPSHOT"
            )
        )]
    if ENDPOINT_BASE_URL_EXTERNAL:
        endpoints.append(
            Endpoint(
                interface='SUBMODEL-1.0RC02', #TODO: why RC02?
                protocolInformation=ProtocolInformation(
                    endpoint_address= ENDPOINT_BASE_URL_EXTERNAL + path + '/' + cx_id + '/submodel?content=value&extent=withBlobValue'
                )
            )
        )
        
    sm = SubmodelDescriptor(
        identification=sm_id,
        id_short=idshort_for_schema(schema=schema),
        semantic_id=Reference(
            value=[schema]
        ),
        endpoints=endpoints,
    )
    return sm


def prepare_submodel_descriptor_list(item: dict, aas_id: str, bpn: str):
    """
    Prepares a list of Submodels from a given item
    """
    cx_id = item.get('catenaXId', None)
    sm_descriptors = []
    for key in list(item.keys()):
        if CX_SCHEMA_LOOKUP_STRING in key:
            sm = prepare_submodel_descriptor(cx_id=cx_id, schema=key, aas_id=aas_id, bpn=bpn)
            sm_descriptors.append(sm)
    return sm_descriptors

def prepare_specific_asset_ids(item):
    """
    Find the SerialPartTypization entry from the item and use the localIdentifiers
    to fill the specificAssetIds for the AAS Registry entry
    """
    sp = get_first_match(item=item, key_match=SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING, default_return=None)
    if len(sp) != 1:
        raise Exception("Length must be exactly 1.")
    if sp:
        return [IdentifierKeyValuePair(**x) for x in sp[0].get('localIdentifiers', []) ] # transform to the typed version of it
    return None


def upsert_registry_entry(item: dict, bpn: str):
    """
    Register the given item in the registry if it doesn't exist yet. Existence check by the
    catenaXId as the globalAssetId.
    """
    cxId = item.get('catenaXId', '')
    if not cxId:
        raise Exception(f"Item does not contain a catenaXId. This is a mandatory field!")
    globalAssetId = cxId
    ga_id_lookup = lookup_by_globalAssetId(globalAssetId)

    if not ga_id_lookup:
        # register a new AAS
        aas_id = upsert_aas_id(cx_id=cxId)
        submodels = prepare_submodel_descriptor_list(item=item, aas_id=aas_id, bpn=bpn)
        specific_asset_ids = prepare_specific_asset_ids(item=item)
        aas_descriptor = AssetAdministrationShellDescriptor(
            identification=aas_id,
            id_short=cxId,
            global_asset_id=Reference(value=[cxId]),
            specific_asset_ids=specific_asset_ids,
            submodel_descriptors=submodels
        )
        data = aas_descriptor.dict()
        #print(json.dumps(data, indent=4))
        r = get_requests_session().post(f"{REGISTRY_BASE_URL}/registry/shell-descriptors", json=data)
        if not r.ok:
            print(f"Could not create AAS. status_code: {r.status_code} content: {r.content}")
            return None
        result = r.json()
        aas_created = AssetAdministrationShellDescriptor(**result)
        print(f"AAS created for cx_id: {cxId} AAS ID: {aas_created.identification} ")
        return aas_created
    else:
        # already exists
        print(f"AAS already exists for cx_id: {cxId} AAS ID: {ga_id_lookup}")

def delete_registry_entry(cx_id: str):
    """
    Returns False if doesn't exist or could not be deleted.
    """
    aas_id = lookup_by_globalAssetId(cx_id)
    if not aas_id:
        print(f"Could not find and delete AAS for cx_id (globalAssetId): {cx_id}")
        return False
    r = get_requests_session().delete(f"{REGISTRY_BASE_URL}/registry/shell-descriptors/{aas_id}")
    if not r.ok:
        print(r.content)
        print(f"Could not delete registry entry for aas_id: {aas_id}")
        return False
    return True
    

def upsert_registry_entry_from_cx_items(bpn: str):
    for item in iterate_cx_items():
        upsert_registry_entry(item, bpn=bpn)

def delete_registry_entry_from_cx_items():
    for cx_item in iterate_cx_items():
        delete_registry_entry(cx_item['catenaXId'])

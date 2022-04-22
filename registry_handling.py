# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/catenax-ng/product-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

import sys
import json
import requests
from aas.registry.models.asset_administration_shell_descriptor import AssetAdministrationShellDescriptor
from aas.registry.models.identifier_key_value_pair import IdentifierKeyValuePair
from aas.registry.models.submodel_descriptor import SubmodelDescriptor
from aas.registry.models.protocol_information import ProtocolInformation
from aas.registry.models.endpoint import Endpoint
from aas.registry.models.reference import Reference
from dependencies import CX_SCHEMA_PREFIX, DB_CX_ITEMS, get_db_item, idshort_for_schema, iterate_cx_items, path_for_schema, unique_id, SCHEMA_SERIAL_PART_TYPIZATION, REGISTRY_BASE_URL
from edc_handling import upsert_aas_id, upsert_sm_id

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
    r = requests.get(f"{REGISTRY_BASE_URL}/lookup/shells", params=query)
    if not r.ok:
        return None
    aas_ids = r.json()
    if len(aas_ids) != 1:
        return None
    return aas_ids[0]

def prepare_edc_submodel_endpoint_address(aas_id: str, sm_id: str):
    """
    # {{providerControlPlaneDockerInternal}}/{{providerBpn}}/{{digitalTwinId}}-{{digitalTwinSubmodelId}}
    """
    return f"providerControlPlaneDockerInternal/providerBpn/{aas_id}-{sm_id}"

def prepare_submodel_descriptor( cx_id: str, schema: str, aas_id: str, endpoint_base_url: str):
    """
    Prepares a Submodel
    """
    path = path_for_schema(schema=schema)
    sm_id = upsert_sm_id(cx_id=cx_id, schema=schema)
    edc_endpoint = prepare_edc_submodel_endpoint_address(aas_id=aas_id, sm_id=sm_id)
    sm = SubmodelDescriptor(
        identification=sm_id,
        id_short=idshort_for_schema(schema=schema),
        semantic_id=Reference(
            value=[schema]
        ),
        endpoints=[
            Endpoint(
                interface='SUBMODEL-1.0RC02',
                protocol_information=ProtocolInformation(
                    endpoint_address=edc_endpoint,
                    endpointProtocol="IDS/ECLIPSE DATASPACE CONNECTOR",
                    endpointProtocolVersion="0.0.1-SNAPSHOT"
                )
            ),
            Endpoint(
                interface='http',
                protocolInformation=ProtocolInformation(
                    endpoint_address= endpoint_base_url + path + '/' + cx_id
                )
            )
        ]
    )
    return sm


def prepare_submodel_descriptor_list(item: dict, aas_id: str, endpoint_base_url: str):
    """
    Prepares a list of Submodels from a given item
    """
    cx_id = item.get('catenaXId', None)
    sm_descriptors = []
    for key in list(item.keys()):
        if key.startswith(CX_SCHEMA_PREFIX):
            sm = prepare_submodel_descriptor(cx_id=cx_id, schema=key, aas_id=aas_id, endpoint_base_url=endpoint_base_url)
            sm_descriptors.append(sm)
    return sm_descriptors


def upsert_registry_entry(item: dict, endpoint_base_url: str):
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
        submodels = prepare_submodel_descriptor_list(item=item, aas_id=aas_id, endpoint_base_url=endpoint_base_url)
        aas_descriptor = AssetAdministrationShellDescriptor(
            identification=aas_id,
            id_short=cxId,
            global_asset_id=Reference(value=[cxId]),
            specific_asset_ids=[IdentifierKeyValuePair(**x) for x in item.get('localIdentifiers', []) ], # transform to the typed version of it
            submodel_descriptors=submodels
        )
        data = aas_descriptor.dict()
        print(json.dumps(data, indent=4))
        r = requests.post(f"{REGISTRY_BASE_URL}/registry/shell-descriptors", json=data)
        if not r.ok:
            print(r.content, file=sys.stderr)
            return None
        result = r.json()
        aas_created = AssetAdministrationShellDescriptor(**result)
        return aas_created
    else:
        # udpate case
        pass

def delete_registry_entry(cx_id: str):
    """
    Returns False if doesn't exist or could not be deleted.
    """
    aas_id = lookup_by_globalAssetId(cx_id)
    if not aas_id:
        print(f"Could not find and delete AAS for cx_id (globalAssetId): {cx_id}")
        return False
    r = requests.delete(f"{REGISTRY_BASE_URL}/registry/shell-descriptors/{aas_id}")
    if not r.ok:
        print(r.content)
        print(f"Could not delete registry entry for aas_id: {aas_id}")
        return False
    return True
    

def upsert_registry_entry_from_cx_items(endpoint_base_url: str):
    for item in iterate_cx_items():
        upsert_registry_entry(item, endpoint_base_url=endpoint_base_url)

def delete_registry_entry_from_cx_items():
    for cx_item in iterate_cx_items():
        delete_registry_entry(cx_item['catenaXId'])

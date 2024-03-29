#!/usr/bin/env python3

import argparse
import logging
import sys
from aas.registry.models.asset_administration_shell_descriptor import AssetAdministrationShellDescriptor
from edc_data_management import EdcDataManagement
import registry_handling as reg
import edc_handling as edc
import aas_helper

from fastapi import FastAPI, Body, Security, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import json
import os
from datetime import datetime
from dependencies import ASSEMBLY_PART_RELATIONSHIP_PATH, settings

app = FastAPI(title='Traceability Case Study Backend')

origins = [
    '*'
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['*'], allow_headers=['*'])

# prepare data directory
CS_ASSEMBLYPARTRELATIONSHIP_DATA_DIR = os.path.join(os.path.dirname(__file__), 'cs-assemblypartrelationship-data')
os.makedirs(CS_ASSEMBLYPARTRELATIONSHIP_DATA_DIR, exist_ok=True)


API_KEY_NAME = 'X-Api-Key'
API_KEY = os.getenv('API_KEY', '1234')
security_api_key = APIKeyHeader(name=API_KEY_NAME, auto_error=True) #auto_error only check if key exists!

def check_api_key(api_key: str = Security(security_api_key)):
    if not api_key == API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Wrong {API_KEY_NAME} value.")


def find(sub_component_entries: list, human_key: str = None, vda_key: str = None):
    """
    Iterates and returns the value for it or None
    """
    for component in sub_component_entries:
        if human_key and component['humanKey'] == human_key:
            return component['value']
        if vda_key and component['vdaKey'] == vda_key:
            return component['value']

@app.post('/', dependencies=[Security(check_api_key)])
def post(body: dict = Body(...)):
    """
    Receives data from the DMC scanning Web App.
    """
    print(json.dumps(body, indent=4))

    child_parts = []
    # supplier parts built into main - first check all of those and raise errors if they don't exist
    for sub in body['sub']:
        artikel_nr = find(sub, human_key='ArtikelNummer') # is the mapping to customerPartId
        chargen_nr = find(sub, human_key='Charge')
        sachnr_hersteller = find(sub, human_key='SachnummerHersteller')

        if not artikel_nr and not sachnr_hersteller:
            msg = f"Sub component does not contain ArtikelNummer or SachnummerHersteller. {json.dumps(sub, indent=4)}"
            logging.error(msg)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=msg)

        if not chargen_nr:
            msg = f"Sub component does not contain Charge. {json.dumps(sub, indent=4)}"
            logging.error(msg)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=msg)


        aas_ids = query_ids(customerPartId=artikel_nr, manufacturerPartId=sachnr_hersteller, partInstanceId=chargen_nr)

        if len(aas_ids) != 1:
            msg = f"Could not find exactly 1 item in the registry for sub component. for artikel_nr: {artikel_nr} sachnummer_hersteller: {chargen_nr} chargen_nr: {chargen_nr}"
            logging.error(msg)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, msg)
        sub_aas_id = aas_ids[0]
        sub_aas = reg.lookup_by_aas_id(sub_aas_id)
        sub_cx_id = get_cx_id_from_aas(aas=sub_aas)
        if not sub_cx_id:
            #TODO
            pass
        now = datetime.now()
        child_parts.append(
            {
                "quantity": {
                    "quantityNumber": 1
                },
                "lifecycleContext" : "AsBuilt",
                "createdOn" : now.isoformat(),
                "lastModifiedOn" : now.isoformat(),
                "childCatenaXId" : sub_cx_id
            }
        )
    print(child_parts)

    # main is our own component
    main = body['main']
    sachnr_hersteller = find(main, human_key='SachnummerHersteller')
    artikel_nr = find(main, vda_key='P') # aka customerPartId
    manufacturer_id = find(main, vda_key='V') # aka manufactuererId (needs mapping to BPN if it is not a BPN yet!)
    chargen_nr = find(main, human_key='Charge')
    main_cx_id = None
    main_submodel_id_apr = None
    main_aas_ids = query_sachnummer(sachnummer_hersteller=sachnr_hersteller, chargen_nr=chargen_nr)
    main_aas_id = None
    main_aas = None

    if len(main_aas_ids) > 1:
        msg = f"more than 1 AAS found for main component artikel_nr: {sachnr_hersteller} and chargen_nr: {chargen_nr}"
        logging.error(msg)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg)

    if len(main_aas_ids) == 1:
        # we just delete it and recreate it - easier for now
        main_aas_id = main_aas_ids[0]
        main_aas = reg.lookup_by_aas_id(aas_id=main_aas_id)
        main_cx_id = aas_helper.get_global_asset_id(aas=main_aas)
        reg.delete_registry_entry_by_aas_id(main_aas_id)

    # default behavior
    local_identifiers = {}
    """
    Details in the CX Spec:
    https://confluence.catena-x.net/pages/viewpage.action?pageId=40502166#id-(TRS)%F0%9F%93%9CDataProvisioning(ImplementationSpecification)-SpecificAssetIDsforSerializedParts
    """
    if manufacturer_id and manufacturer_id.startswith('BPN'):
        local_identifiers['manufacturerId'] = manufacturer_id
    else:
        if not settings.my_bpn:
            msg = f"BPN not known. Please consult your application admin to configure env MY_BPN."
            logging.error(msg)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=msg)
        local_identifiers['manufacturerId'] = settings.my_bpn

    if sachnr_hersteller:
        local_identifiers['manufacturerPartId'] = sachnr_hersteller

    if artikel_nr:
        local_identifiers['customerPartId'] = artikel_nr

    if chargen_nr:
        local_identifiers['partInstanceId'] = chargen_nr

    if not main_cx_id:
        main_cx_id = aas_helper.generate_uuid()
    aas = aas_helper.build_aas(local_identifiers=local_identifiers, aas_id=main_aas_id, cx_id=main_cx_id)
    main_submodel_id_apr = aas_helper.generate_uuid() # I think we don't need to stre this - we only need this further down to create the edc asset
    apr_edc_endpoint = reg.prepare_edc_submodel_endpoint_address(aas_id=aas.identification, sm_id=main_submodel_id_apr)
    submodel = aas_helper.build_submodel(endpoint=apr_edc_endpoint)
    aas.submodel_descriptors = [submodel]
    print(aas)
    aas_result = reg.create(aas=aas)

    # now let's prepare the data for the actual submodel endpoint
    store_submodel_data(main_cx_id=main_cx_id, child_parts=child_parts)

    # and finnally create the EDC assets for our endpoint
    edc_asset_id = f"{aas.identification}-{main_submodel_id_apr}"
    backend_data_source_endpoint = build_backend_data_source_endpoint(main_cx_id=main_cx_id)
    edc_result = create_edc_asset(asset_id=edc_asset_id, endpoint=backend_data_source_endpoint)
    print(edc_result)

    result = {
        'aas_id': aas_result.identification,
        **edc_result
    }
    print(result)
    return result


@app.get(ASSEMBLY_PART_RELATIONSHIP_PATH + '/{catenaXId}', dependencies=[Security(check_api_key)])
async def get_assembly_part_relationship(catenaXId: str, content: str = Query(example='value', default=None), extent: str = Query(example='withBlobValue', default=None)):
    logging.debug(f"get_assembly_part_relationship catenaXId: {catenaXId}")
    if '/' in catenaXId or '.' in catenaXId:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="ID contains invalid chars") # basic security check against relative path issue
    fn = os.path.join(CS_ASSEMBLYPARTRELATIONSHIP_DATA_DIR, catenaXId) # after the check this should be ok, not perfect, but ok
    if not os.path.isfile(fn):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"No data found for cx_id: {catenaXId}")
    data = ''
    with (open(fn, 'r')) as f:
        data = f.read()

    child_data = json.loads(data)
    apr = {
        'catenaXId': catenaXId,
        'childParts': child_data
    }

    return apr

def store_submodel_data(main_cx_id: str, child_parts):
    """
    Store data on disk for later retrieval via the submodel endpoint.
    """
    data = {
        "catenaXId": main_cx_id,
        "childParts": child_parts,
    }
    sub_data = json.dumps(data)
    fn = os.path.join(CS_ASSEMBLYPARTRELATIONSHIP_DATA_DIR, main_cx_id)
    with (open(fn, 'w')) as f:
        f.write(sub_data)

def create_edc_asset(asset_id: str, endpoint: str):
    """
    Creates the EDC relevat parts, that includes, asset, policy, contractdefinition

    endpoint: backend / data source endpoint
    """
    dm = EdcDataManagement(
            data_management_base_url=settings.edc_base_url,
            data_management_auth_key='X-Api-Key',
            data_management_auth_code=settings.provider_edc_api_key,
            backend_auth_key=API_KEY_NAME,
            backend_auth_code=API_KEY
    )
    if dm.exists(asset_id=asset_id):
        print('exists already')
    return dm.create_asset_and_friends(asset_id=asset_id, endpoint=endpoint)

def build_backend_data_source_endpoint(main_cx_id):
    return f"{settings.cs_backend_base_url}{ASSEMBLY_PART_RELATIONSHIP_PATH}/{main_cx_id}"

def get_cx_id_from_aas(aas):
    try:
        return aas['globalAssetId']['value'][0]
    except:
        return None

def query_ids(customerPartId: str, manufacturerPartId:str, partInstanceId: str):
    query = []
    if customerPartId:
        query.append(
            {
                'key': 'customerPartId',
                'value': customerPartId,
            }
        )

    if manufacturerPartId:
        query.append(
            {
                'key': 'manufacturerPartId',
                'value': manufacturerPartId,
            }
        )

    if partInstanceId:
        query.append(
            {
                'key': 'partInstanceId',
                'value': partInstanceId
            }
        )
    aas_ids = reg.discover(query1=query)
    return aas_ids

def query_customerPartId_partInstanceId(customerPartId: str, partInstanceId: str):
    query = []
    query.append(
        {
            'key': 'customerPartId',
            'value': customerPartId,
        }
    )
    query.append(
        {
            'key': 'partInstanceId',
            'value': partInstanceId
        }
    )
    aas_ids = reg.discover(query1=query)
    return aas_ids



def query_sachnummer(sachnummer_hersteller: str, chargen_nr: str):
    query = []
    if sachnummer_hersteller:
        query.append(
            {
                'key': 'manufacturerPartId',
                'value': sachnummer_hersteller,
            }
        )
    if chargen_nr:
        query.append(
            {
                'key': 'partInstanceId',
                'value': chargen_nr
            }
        )
    aas_ids = reg.discover(query1=query)
    return aas_ids

def query_artikel_nr(artikel_nr: str, chargen_nr: str):
    query = []
    if artikel_nr:
        query.append(
            {
                'key': 'customerPartId',
                'value': artikel_nr,
            }
        )
    if chargen_nr:
        query.append(
            {
                'key': 'partInstanceId',
                'value': chargen_nr
            }
        )
    aas_ids = reg.discover(query1=query)
    return aas_ids

def delete_from_registry():
    """
    Look into the data directory and from the file names (cx_id) know which elements
    from the registry to delete.
    """
    files = os.listdir(CS_ASSEMBLYPARTRELATIONSHIP_DATA_DIR)
    for file in files:
        if not file.startswith('urn:uuid:'):
            continue
        cx_id = file
        deleted = reg.delete_registry_entry(cx_id=cx_id)
        print(deleted)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Traceability Case Study Backend. Start without any args to start the server.")
    # bool argument python 3.9 backward compatible way
    parser.add_argument('--delete-registry', action='store_true', default=False,
            help='Delete AAS elements known to this backend from the registry (by cx_id)')
    
    args = parser.parse_args()
    if args.delete_registry:
        delete_from_registry()
        sys.exit()

    import uvicorn
    port = os.getenv('PORT', '8080')
    workers = os.getenv('WORKERS', '3')
    uvicorn.run("case-study:app", host="0.0.0.0", port=int(port), workers=int(workers), reload=False)

#!/usr/bin/env python3

from email.policy import default
import sys
import time
import json
from uuid import uuid4
import jq
from urllib.parse import urlparse
import click
import requests
from requests.auth import HTTPBasicAuth
from edc_handling import prepare_edc_headers
import registry_handling
from dependencies import settings
import importer


print(json.dumps(settings.dict(), indent=4))

@click.group(help='Helper tool to use aas-proxy')
def cli():
    pass

@cli.group(help='Search for AAS ID or GlobalAssetID')
def search():
    pass

@search.command('aas')
@click.option('-ea', '--print-edc-assets', default=False, is_flag=True)
@click.argument('aas_id')
def search_aas(aas_id, print_edc_assets):
    print(aas_id)
    aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
    if print_edc_assets:
        print_out_edc_assets(aas)
    else:
        print(json.dumps(aas, indent=4))

def print_out_edc_assets(aas_obj):
    """
    Prints out the EDC asset_id from a given AAS object
    """
    for sm in jq.compile(".submodelDescriptors[].endpoints[0].protocolInformation.endpointAddress").input(aas_obj):
        #print(sm)
        edc_info = extract_edc_information(sm)
        print(edc_info)

def extract_edc_information(submodel_descriptor_endpoint_url: str):
    """
    Extracts the asset_id from a given URL
    """
    url = urlparse(submodel_descriptor_endpoint_url)
    bpn = url.path.split('/')[1]
    edc_asset_id = url.path.split('/')[2]
    connector_endpoint = url.scheme + '://' + url.netloc
    return {'bpn': bpn, 'edc_asset_id': edc_asset_id, 'connector_ednpoint': connector_endpoint}


@search.command('asset')
@click.argument('global_asset_id')
def search_asset(global_asset_id):
    print(global_asset_id)
    aas_ids = registry_handling.lookup_by_globalAssetIds_all(global_asset_id)
    for aas_id in aas_ids:
        print(aas_id)

@search.command('all')
def search_all(aas_proxy):
    all = registry_handling.get_all()
    for aas in all:
        print(json.dumps(aas, indent=4))
        input("")

# edc
@cli.group(help='Fetch from EDC')
def edc():
    pass

@edc.command('negotiate')
@click.argument('connector_endpoint')
@click.argument('edc_asset_id')
def edc_negotiate(connector_endpoint, edc_asset_id):

    url = f"{settings.consumer_control_plane_base_url}/api/v1/data/control/catalog?provider=http://cxdev.germanywestcentral.cloudapp.azure.com:8185"
    #url = f"{settings.consumer_control_plane_base_url}/api/v1/data/catalog?providerUrl=http://cxdev.germanywestcentral.cloudapp.azure.com:8185"
    r = requests.get(url, headers=prepare_edc_headers())
    j = r.json()
    print(json.dumps(j, indent=4))

    data = {
        'connectorId': 'urn:connector:control.cxtesting.germanywestcentral.cloudapp.azure.com',
        'connectorAddress': connector_endpoint,
        'protocol': 'ids-multipart',
        'offer': {
            'offerId': str(uuid4()),
            'assetId': edc_asset_id,
            'policy': {
                'permissions': [
                    {
                        "edctype": "dataspaceconnector:permission",
                        'target': edc_asset_id,
                        'action': {
                            'type': 'USE'
                        }
                    }
                ]
            }
        }
    }
    #url = f"{settings.consumer_control_plane_base_url}/api/v1/data/contractdefinitions"
    url = f"{settings.consumer_control_plane_base_url}/api/v1/data/contractnegotiations"
    r = requests.post(url, json=data, headers=prepare_edc_headers())
    if not r.ok:
        print(f"Could not init negotiations. Error: {r.content}")
        sys.exit(-1)
    j = r.json()
    negotiation_id = j['id']

    url = f"{settings.consumer_control_plane_base_url}/api/v1/data/contractnegotiations/{negotiation_id}"
    while(True):
        r = requests.get(url, headers=prepare_edc_headers())
        j = r.json()
        print(json.dumps(j, indent=4))
        time.sleep(2)


    print(r.content)

# fetch
@cli.group(help='Fetch endpoint data')
def fetch():
    pass

def get_endpoint_for(aas, endpoint_type: str):
    """
    Since AAS-Proxy bug https://github.com/catenax-ng/catenax-at-home/issues/46

    we use idShort for now to identify the right endpoint

    TODO: needs to be fixed.
    TODO: Is this really a list of endpoints?
    """
    for sm in aas['submodelDescriptors']:
        if sm['idShort'] == endpoint_type:
            return sm['endpoints'][0]['protocolInformation']['endpointAddress']
    return None

def fetch_for(aas_id: str, sm_type: str):
    """
    given AAS ID
    """
    aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
    return fetch_for_aas(aas=aas, sm_type=sm_type)

def fetch_for_aas(aas, sm_type: str):
    """
    given AAS (not only aas id)
    """
    if not aas:
        print(f"Could not find aas for aas_id: {aas_id}")
        sys.exit(-1)
    url = get_endpoint_for(aas=aas, endpoint_type=sm_type)
    start = time.time()
    url_parts = urlparse(url)
    path_parts = url_parts.path.split('/')
    path = str.join('/', path_parts[2:])
    #wrapper_url = f"{settings.api_wrapper_base_url}/{path}?provider-connector-url={url_parts.scheme}://{url_parts.netloc}/{path_parts[1]}"
    #wrapper_url = f"{settings.api_wrapper_base_url}/{path}?provider-connector-url={url_parts.scheme}://{url_parts.netloc}"
    wrapper_url = f"{settings.api_wrapper_base_url}/{path}?content=value&extent=withBlobValue&provider-connector-url={url_parts.scheme}://{url_parts.netloc}"

    r = requests.get(wrapper_url, auth=HTTPBasicAuth(settings.wrapper_basic_auth_user, settings.wrapper_basic_auth_password))
    end = time.time()
    duration = end - start
    print(f"call execution time: {duration}")
    if not r.ok:
        print(r.content)
        sys.exit(-1)
    j = r.json()
    print(json.dumps(j, indent=4))

@fetch.command('SerialPartTypization')
@click.argument('aas_id')
def fetch_serial_part_typization(aas_id):
    data = fetch_for(aas_id=aas_id, sm_type='serialPartTypization')
    print(json.dumps(data, indent=4))

@fetch.command('AssemblyPartRelationship')
@click.argument('aas_id')
def fetch_assembly_part_relationship(aas_id, aas_proxy):
    fetch_for(aas_id=aas_id, sm_type='assemblyPartRelationship', aas_proxy=aas_proxy)

@fetch.command('MaterialForRecycling')
@click.argument('aas_id')
def fetch_material_for_recycling(aas_id, aas_proxy):
    fetch_for(aas_id=aas_id, sm_type='materialForRecycling', aas_proxy=aas_proxy)

@fetch.command('EdcAssetId')
@click.argument('edc_asset_id')
def fetch_edc_asset(edc_asset_id):
    url = f"{settings.consumer_control_plane_url}/api/v1/data/contractnegotiations"


#####
# fetch via api-wrapper directly
#####
@fetch.command('api-wrapper')
@click.argument('connector_url')
@click.argument('edc_asset_id')
def fetch_edc_asssubUrlet_via_wrapper(connector_url, edc_asset_id):
    # needs api-wrapper endpoint from config
    params = {
        'content': 'value',
        'extent': 'withBlobValue',
        'provider-connector-url': connector_url
    }
    url = f"{settings.api_wrapper_base_url}/{edc_asset_id}/submodel"
    print(f"fetch_edc_asssubUrlet_via_wrapper: {url} \n params: {params}")
    r = requests.get(
        url,
        auth=HTTPBasicAuth(settings.wrapper_basic_auth_user, settings.wrapper_basic_auth_password),
        params=params,
    )
    j = r.json()
    print(print(json.dumps(j, indent=4)))

#####
# testdata management
####

@cli.group(help='Manage Testdata files')
def testdata():
    pass

@testdata.command('bpns', help='List all BPNs from the given testdata file')
@click.argument('testdata_file')
def list_bpns(testdata_file):
    data = importer.get_testdata_from_file(testdata_file)
    bpns = importer.get_manufacturers(testdata=data)
    print(bpns)

@testdata.command('cxids', help='List all CX IDs for a given BPN from the given testdata file')
@click.option('-a', '--show-aas-id', default=False, is_flag=True)
@click.option('-s', '--show-serial-part-typization', default=False, is_flag=True)
@click.argument('testdata_file')
@click.argument('BPN')
def list_cxids(testdata_file, bpn, show_aas_id, show_serial_part_typization):
    data = importer.get_testdata_from_file(testdata_file)
    for item in importer.iterate_bpn_aspects(testdata=data, bpn=bpn):
        cxid = item.get('catenaXId', '')
        print(cxid)
        aas_id = None
        if show_aas_id or show_serial_part_typization:
            aas_id = registry_handling.lookup_by_globalAssetId(globalAssetId=cxid)
        if show_aas_id:
            print(f"aas_id: {aas_id}")
        if show_serial_part_typization:
            fetch_for(aas_id=aas_id, sm_type='serialPartTypization')


if __name__ == '__main__':
    cli()
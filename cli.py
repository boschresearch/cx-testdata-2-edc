#!/usr/bin/env python3

from email.policy import default
import logging
import sys
import time
import json
from uuid import uuid4
import jq
from urllib.parse import urlparse
import click
import requests
from requests.auth import HTTPBasicAuth
from aas.registry.models.asset_administration_shell_descriptor import AssetAdministrationShellDescriptor
from edc_handling import prepare_edc_headers_consumer, prepare_edc_headers_provider
import registry_handling
import aas_helper
from dependencies import settings
import importer
from aas_helper import extract_edc_information



@click.group(help='Helper tool to use aas-proxy')
def cli():
    pass

@cli.group(help='Search for AAS ID or CxId')
def search():
    pass

@search.command('aas')
@click.option('-ea', '--print-edc-assets', default=False, is_flag=True)
@click.argument('aas_id')
def search_aas(aas_id, print_edc_assets):
    logging.info(f"search_aas() aas_id: {aas_id}")
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

@search.command('cxid')
@click.argument('cxid')
def search_asset(cxid):
    logging.info(f"search_asset() cxid: {cxid}")
    aas_ids = registry_handling.lookup_by_globalAssetIds_all(cxid)
    for aas_id in aas_ids:
        print(f"cxid: {cxid} -> aas_id: {aas_id}")

@search.command('all')
def search_all():
    all = registry_handling.get_all(page_size=1000000000)
    for aas in all:
        print(json.dumps(aas, indent=4))
        input("")

@search.command('bpn', help='Find all Registry items for a given BPN')
@click.option('--csv', default=False, is_flag=True)
@click.argument('bpn')
def search_for_bpn(bpn: str, csv):
    logging.info(f"Searching for BPN: {bpn}")
    aas_ids = registry_handling.discover_via_bpn(bpn)

    if csv:
        # print header
        print(f"aas_id,cx_id,SerialPartTypizationEndpoint,AssemblyPartRelationshipEndpoint")

    for aas_id in aas_ids:
        if csv:
            aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
            cx_id = aas_helper.get_global_asset_id(aas)
            #aas_shell = AssetAdministrationShellDescriptor.parse_obj(aas)
            spt_endpoint = registry_handling.get_endpoint_for(aas, 'serialPartTypization')
            apr_endpoint = registry_handling.get_endpoint_for(aas, 'assemblyPartRelationship')
            print(f"{aas['identification']},{cx_id},{spt_endpoint},{apr_endpoint}")
        else:
            print(aas_id)

@search.command('stat', help="Statistics - Fetch AAS endpoints and output list with results.")
@click.option('--sm-type', default='serialPartTypization', help='assemblyPartRelationship default:serialPartTypization')
@click.option('--bpn', help="For a given BPN", default="")
def search_all_stat(bpn:str, sm_type: str):
    stat = {
        'ok': {},
        'not_ok': {},
        'ok_aas_ids': [],
        'not_ok_aas_ids': [],
        'items': 0,
    }
    #sm_type='assemblyPartRelationship'
    all = []
    if bpn:
        aas_ids = registry_handling.discover_via_bpn(bpn)
        for aas_id in aas_ids:
            aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
            all.append(aas)
    else:
        all = registry_handling.get_all(page_size=10000000)
    stat['items'] = len(all)
    for aas in all:
        #print(json.dumps(aas, indent=4))
        try:
            url = registry_handling.get_endpoint_for(aas=aas, endpoint_type=sm_type)
            """
            if not "cxdev" in url:
                print(url)
                continue
            """
            if not url:
                continue # means there is not serialPartTypization submodel in the AAS
            url_parts = urlparse(url)
            host = url_parts.netloc

            try:
                data = fetch_for_aas(aas=aas, sm_type=sm_type)
                #data = fetch_for(aas_id=aas['identification'], sm_type='serialPartTypization', aas_proxy=False)
                #print(data)
                stat['ok'][host] = stat['ok'].get(host, 0) + 1
                stat['ok_aas_ids'].append(aas['identification'])
                print(f"ok: {host}")
            except Exception as fetch_ex:
                stat['not_ok'][host] = stat['not_ok'].get(host, 0) + 1
                stat['not_ok_aas_ids'].append(aas['identification'])
                #print(f"not_ok: {aas['identification']}")
                logging.error(fetch_ex)
        except Exception as ex:
            logging.error(ex)
    print(stat)


# edc
@cli.group(help='Fetch from EDC')
def edc():
    pass

@edc.command('catalog')
def edc_get_catalog():
    pass

@edc.command('list_assets')
def edc_list_assets():
    params = {
        'limit': 1000,
    }
    url = f"{settings.edc_base_url}/assets"
    r = requests.get(url, headers=prepare_edc_headers_provider(), params=params)
    if not r.ok:
        logging.error(f"Could not fetch list of assets. Reason: {r.reason} Content: {r.content}")
        sys.exit()
    print(json.dumps(r.json(), indent=4))

@edc.command('list_policies')
def edc_list_policies():
    url = f"{settings.edc_base_url}/policies"
    r = requests.get(url, headers=prepare_edc_headers_provider())
    if not r.ok:
        logging.error(f"Could not fetch list of policies. Reason: {r.reason} Content: {r.content}")
        sys.exit()
    print(json.dumps(r.json(), indent=4))


@edc.command('negotiate')
@click.argument('connector_endpoint')
@click.argument('edc_asset_id')
def edc_negotiate(connector_endpoint, edc_asset_id):

    url = f"{settings.consumer_control_plane_base_url}/api/v1/data/control/catalog?provider=http://cxdev.germanywestcentral.cloudapp.azure.com:8185"
    #url = f"{settings.consumer_control_plane_base_url}/api/v1/data/catalog?providerUrl=http://cxdev.germanywestcentral.cloudapp.azure.com:8185"
    r = requests.get(url, headers=prepare_edc_headers_consumer())
    j = r.json()
    logging.info(json.dumps(j, indent=4))

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
    r = requests.post(url, json=data, headers=prepare_edc_headers_consumer())
    if not r.ok:
        logging.error(f"Could not init negotiations. Error: {r.content}")
        sys.exit(-1)
    j = r.json()
    negotiation_id = j['id']

    url = f"{settings.consumer_control_plane_base_url}/api/v1/data/contractnegotiations/{negotiation_id}"
    while(True):
        r = requests.get(url, headers=prepare_edc_headers_consumer())
        j = r.json()
        print(json.dumps(j, indent=4))
        time.sleep(2)


    print(r.content)

# fetch
@cli.group(help='Fetch endpoint data')
def fetch():
    pass

def fetch_for(aas_id: str, sm_type: str):
    """
    given AAS ID
    """
    aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
    return fetch_for_aas(aas=aas, sm_type=sm_type)

def fetch_for_aas(aas, sm_type: str):
    return fetch_for_aas_type_list(aas, [sm_type])

def fetch_for_aas_type_list(aas, sm_types):
    """
    given AAS (not only aas id)

    Tries to find the first endpont from the given list of types.
    Relevant for serialPartTypization vs Batch. First match is returned.
    """
    if not aas:
        raise Exception(f"AAS not given")
    url = None
    for sm_type in sm_types:
        url = registry_handling.get_endpoint_for(aas=aas, endpoint_type=sm_type)
        if url:
            break
    start = time.time()
    url_parts = urlparse(url)
    path_parts = url_parts.path.split('/')
    if path_parts[1].lower().startswith('bpn'):
        bpn = path_parts[1]
        path = str.join('/', path_parts[2:])
        wrapper_url = f"{settings.api_wrapper_base_url}/{path}?content=value&extent=withBlobValue&provider-connector-url={url_parts.scheme}://{url_parts.netloc}/{bpn}"
    else:
        # no BPN in path
        #bpn = path_parts[1]
        path = str.join('/', path_parts[1:])
        wrapper_url = f"{settings.api_wrapper_base_url}/{path}?content=value&extent=withBlobValue&provider-connector-url={url_parts.scheme}://{url_parts.netloc}"

    r = requests.get(wrapper_url, auth=HTTPBasicAuth(settings.wrapper_basic_auth_user, settings.wrapper_basic_auth_password))
    end = time.time()
    duration = end - start
    logging.info(f"call execution time: {duration}")
    if not r.ok:
        raise Exception(f"Could not fetch data from url: {wrapper_url}. Result: {r.content}")
    j = r.json()
    return j

@fetch.command('SerialPartTypization')
@click.option('-f', '--file-name', default=None)
@click.option('-b', '--bpn', default=None)
@click.argument('aas_id', default=None, required=False)
def fetch_serial_part_typization(aas_id: str, file_name: str, bpn: str):
    if aas_id:
        aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
        data = fetch_for_aas_type_list(aas, sm_types=['serialPartTypization', 'Batch'])
        print(json.dumps(data, indent=4))
    if file_name:
        with open(file_name, 'r') as f:
            lines = f.readlines()
            aas_ids = []
            for l in lines:
                parts = l.split('AAS ID:')
                aas_id = parts[1].strip()
                aas_ids.append(aas_id)
            fetch_for_aas_ids(aas_ids=aas_ids, sm_types=['serialPartTypization', 'Batch'])

    if bpn:
        # first find all relevant AAS
        aas_ids = registry_handling.discover_via_bpn(bpn)
        fetch_for_aas_ids(aas_ids=aas_ids, sm_types=['serialPartTypization', 'Batch'])

def fetch_for_aas_ids(aas_ids, sm_types):
    failed = []
    good = []

    for aas_id in aas_ids:
        try:
            aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
            data = fetch_for_aas_type_list(aas, sm_types=sm_types)
        except Exception as ex:
            failed.append(aas_id)
            logging.error(f"failed to fetch for aas_id: {aas_id}")
            print(f"failed to fetch for aas_id: {aas_id}")
            continue
        print(json.dumps(data, indent=4))
        good.append(aas_id)
    print(f"good: {good}")
    print(f"failed: {failed}")
    print(f"numbers: good items: {len(good)} failed items: {len(failed)}")



@fetch.command('AssemblyPartRelationship')
@click.argument('aas_id')
def fetch_assembly_part_relationship(aas_id):
    data = fetch_for(aas_id=aas_id, sm_type='assemblyPartRelationship')
    print(json.dumps(data, indent=4))

@fetch.command('MaterialForRecycling')
@click.argument('aas_id')
def fetch_material_for_recycling(aas_id):
    data = fetch_for(aas_id=aas_id, sm_type='materialForRecycling')
    print(json.dumps(data, indent=4))

@fetch.command('EdcAssetId')
@click.argument('edc_asset_id')
def fetch_edc_asset(edc_asset_id):
    url = f"{settings.consumer_control_plane_url}/api/v1/data/contractnegotiations"

@fetch.command('catalog')
@click.option('--out-file', help='output file path')
#@click.option('--api-wrapper', help='Use api-wrapper instead of consumer edc')
@click.argument('endpoint')
def fetch_catalog(endpoint, out_file):
    params = {
        'providerUrl': f"{endpoint}/api/v1/ids/data",
        'limit': 1000000000,
    }
    r = requests.get(f"{settings.consumer_control_plane_base_url}/api/v1/data/catalog", params=params, headers=prepare_edc_headers_consumer())
    if not r.ok:
        logging.error(f"Could not fetch catalog. Reason: {r.reason} Content: {r.content}")
    j = r.json()
    j_str = json.dumps(j, indent=4)
    if out_file:
        with open(out_file, 'w') as f:
            f.write(j_str)
    print(j_str)

#####
# fetch via api-wrapper directly
#####
@fetch.command('api-wrapper')
@click.option('-r', '--raw-data', default=False, is_flag=True)
@click.argument('connector_url')
@click.argument('edc_asset_id')
def fetch_edc_asssubUrlet_via_wrapper(connector_url, edc_asset_id, raw_data):
    # needs api-wrapper endpoint from config
    params = {
        'provider-connector-url': connector_url
    }
    url = f"{settings.api_wrapper_base_url}/{edc_asset_id}/xxx" # api-wrapper needs the something behind /
    if not raw_data:
        # assuming AAS Submodel with required params
        params['content'] = 'value'
        params['extent'] = 'withBlobValue'
        url = f"{settings.api_wrapper_base_url}/{edc_asset_id}/submodel"

    logging.info(f"fetch_edc_asssubUrlet_via_wrapper: {url} \n params: {params}")
    r = requests.get(
        url,
        auth=HTTPBasicAuth(settings.wrapper_basic_auth_user, settings.wrapper_basic_auth_password),
        params=params,
    )
    if not r.ok:
        logging.error(f"could not fetch data. Reason: {r.reason} Content: {r.content}")
    if not raw_data:
        j = r.json()
        print(print(json.dumps(j, indent=4)))
    else:
        print(r.content)

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
        logging.info(f"cxid: {cxid}")
        aas_id = None
        if show_aas_id or show_serial_part_typization:
            aas_id = registry_handling.lookup_by_globalAssetId(globalAssetId=cxid)
        if show_aas_id:
            logging.info(f"aas_id: {aas_id}")
        if show_serial_part_typization:
            fetch_for(aas_id=aas_id, sm_type='serialPartTypization')


@cli.group(help='Cleanup')
def cleanup():
    pass

@cleanup.command('registry')
@click.argument('bpn')
def cleanup_registry(bpn: str):
    aas_ids = registry_handling.discover_via_bpn(bpn)
    for aas_id in aas_ids:
        aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
        print(json.dumps(aas, indent=4))
        print("Delete? 'n' to not or any other key to continue or Strg+c to cancel)")
        confirmation = sys.stdin.read(1) # only 1 char
        if confirmation == 'n':
            continue
        deleted = registry_handling.delete_registry_entry_by_aas_id(aas_id=aas_id)
        print("Deleting...")
        if not deleted:
            print(f"Could not delete registry item for aas_id: {aas_id}")
            print(f"Confirm with key press...")
            sys.stdin.read(1) # get read confirmation ;-)
        else:
            print(f"Registry item deleted.")

if __name__ == '__main__':
    FORMAT = '%(asctime)s %(funcName)s %(message)s'
    logging.basicConfig(filename='log.log', level=logging.DEBUG, format=FORMAT)
    settings_dump = json.dumps(settings.dict(), indent=4)
    logging.info(f"settings: {settings_dump}")
    cli()
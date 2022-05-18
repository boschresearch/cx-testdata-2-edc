#!/usr/bin/env python3

from email.policy import default
import sys
import time
import json
import jq
from urllib.parse import urlparse
from textwrap import indent
from urllib import request
import click
import requests
from requests.auth import HTTPBasicAuth
import registry_handling
from dependencies import settings


def use_proxy():
    # we change our default registry endpoint to gro through the aas proxy
    # if you want to go directly to the registry, set the according env to ''
    if settings.consumer_aas_proxy_base_url:
        print(f"Old registry_base_url: {settings.registry_base_url}")
        settings.registry_base_url = settings.consumer_aas_proxy_base_url
        print(f"New registry_base_url: {settings.registry_base_url}")

print(json.dumps(settings.dict(), indent=4))

@click.group(help='Helper tool to use aas-proxy')
def cli():
    pass

@cli.group(help='Search for AAS ID or GlobalAssetID')
def search():
    pass

@search.command('aas')
@click.option('-p', '--aas-proxy', default=False, is_flag=True)
@click.option('-ea', '--print-edc-assets', default=False, is_flag=True)
@click.argument('aas_id')
def search_aas(aas_id, aas_proxy, print_edc_assets):
    print(aas_id)
    if aas_proxy:
        use_proxy()
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
@click.option('-p', '--aas-proxy', default=False, is_flag=True)
@click.argument('global_asset_id')
def search_asset(global_asset_id, aas_proxy):
    print(global_asset_id)
    if aas_proxy:
        use_proxy()
    aas_ids = registry_handling.lookup_by_globalAssetIds_all(global_asset_id)
    for aas_id in aas_ids:
        print(aas_id)

@search.command('all')
@click.option('-p', '--aas-proxy', default=False, is_flag=True)
def search_all(aas_proxy):
    if aas_proxy:
        use_proxy()
    all = registry_handling.get_all()
    for aas in all:
        print(json.dumps(aas, indent=4))
        input("")

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
    aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
    url = get_endpoint_for(aas=aas, endpoint_type=sm_type)
    start = time.time()
    r = requests.get(url, auth=HTTPBasicAuth(settings.wrapper_basic_auth_user, settings.wrapper_basic_auth_password))
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
    fetch_for(aas_id=aas_id, sm_type='serialPartTypization')

@fetch.command('AssemblyPartRelationship')
@click.argument('aas_id')
def fetch_assembly_part_relationship(aas_id):
    fetch_for(aas_id=aas_id, sm_type='assemblyPartRelationship')

@fetch.command('MaterialForRecycling')
@click.argument('aas_id')
def fetch_material_for_recycling(aas_id):
    fetch_for(aas_id=aas_id, sm_type='materialForRecycling')

@fetch.command('EdcAssetId')
@click.argument('edc_asset_id')
def fetch_edc_asset(edc_asset_id):
    url = f"{settings.consumer_control_plane_url}/api/v1/data/contractnegotiations"

if __name__ == '__main__':
    cli()
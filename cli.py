#!/usr/bin/env python3

import sys
import time
import json
from textwrap import indent
from urllib import request
import click
import requests
from requests.auth import HTTPBasicAuth
import registry_handling
from dependencies import settings


# we change our default registry endpoint to gro through the aas proxy
# if you want to go directly to the registry, set the according env to ''
if settings.consumer_aas_proxy_base_url:
    settings.registry_base_url = settings.consumer_aas_proxy_base_url

print(json.dumps(settings.dict(), indent=4))

@click.group(help='Helper tool to use aas-proxy')
def cli():
    pass

@cli.group(help='Search for AAS ID or GlobalAssetID')
def search():
    pass

@search.command('aas')
@click.argument('aas_id')
def search_aas(aas_id):
    print(aas_id)
    aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
    print(json.dumps(aas, indent=4))

@search.command('asset')
@click.argument('global_asset_id')
def search_asset(global_asset_id):
    print(global_asset_id)
    aas_ids = registry_handling.lookup_by_globalAssetIds_all(global_asset_id)
    for aas_id in aas_ids:
        print(aas_id)

@search.command('all')
def search_all():
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
    fetch_for(aas_id=aas_id, sm_type='SerialPartTypization')

@fetch.command('AssemblyPartRelationship')
@click.argument('aas_id')
def fetch_assembly_part_relationship(aas_id):
    fetch_for(aas_id=aas_id, sm_type='AssemblyPartRelationship')

@fetch.command('MaterialForRecycling')
@click.argument('aas_id')
def fetch_material_for_recycling(aas_id):
    fetch_for(aas_id=aas_id, sm_type='MaterialForRecycling')

if __name__ == '__main__':
    cli()
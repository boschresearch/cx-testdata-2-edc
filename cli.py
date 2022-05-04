#!/usr/bin/env python3

import json
from textwrap import indent
import click
import registry_handling
from dependencies import settings


# we change our default registry endpoint to gro through the aas proxy
# if you want to go directly to the registry, set the according env to ''
if settings.consumer_aas_proxy_base_url:
    settings.registry_base_url = settings.consumer_aas_proxy_base_url

print(json.dumps(settings.dict(exclude={'client_secret_registry'}), indent=4))

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
        aas = registry_handling.lookup_by_aas_id(aas_id=aas_id)
        print(json.dumps(aas, indent=4))
        input("Press key to continue...")

@search.command('all')
def search_all():
    all = registry_handling.get_all()
    for aas in all:
        print(json.dumps(aas, indent=4))
        input("")



if __name__ == '__main__':
    cli()
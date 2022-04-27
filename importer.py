# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/catenax-ng/product-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

import shelve
import sys
import os
import argparse
import json
import shelve

from registry_handling import delete_registry_entry_from_cx_items, upsert_registry_entry_from_cx_items
from edc_handling import delete_assets_from_cx_items, upsert_assets_from_cx_items
from dependencies import REGISTRY_BASE_URL, DB_CX_ITEMS, SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING, SCHEMA_TESTDATA_CONTAINER_LOOKUP_STRING, delete_db_all, get_first_match


parser = argparse.ArgumentParser(description="Import from test data set (JSON)")
parser.add_argument('input_filename',
        help='Input file. needs to be in format of TestDataContainer/1.0.0')
parser.add_argument('--list-manufacturers', action='store_true',
        help='List available ManufactuerID s')
parser.add_argument('--import-for',
        help='Import data for the given ManufactuerID')
parser.add_argument('--disable-registry-entry', action='store_true',
        help='Disables automatic registering at the AAS registry. (relevant env: REGISTRY_BASE_URL)')
parser.add_argument('--delete',action='store_true', default=False,
        help='Deletes items from EDC and Registry. Can not be combined with import, but also needs the Manufacturer ID.')


args = parser.parse_args()
print(args)

if not args.input_filename:
    parser.print_help()
    sys.exit(1)

if not os.path.isfile(args.input_filename):
    print(f"Given input file does not exist: {args.input_filename}", file=sys.stderr)
    sys.exit(1)

# read the data
manufacturers = set()
filedata = ''
with open(args.input_filename, 'r', encoding='iso-8859-1') as f:
    filedata = f.read()
data = json.loads(filedata)

testdata = get_first_match(data, key_match=SCHEMA_TESTDATA_CONTAINER_LOOKUP_STRING, default_return=[])

if args.list_manufacturers:
    for item in testdata:
        part_typizations = get_first_match(item=item, key_match=SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING, default_return=[])
        for aspect in part_typizations:
            for localid in aspect['localIdentifiers']:
                if localid.get('key', '') == 'ManufacturerID':
                    manufacturers.add(localid.get('value', ''))
    print(manufacturers)

if args.import_for:
    manufacturer = args.import_for
    db_items = {}

    
    for item in testdata:
        part_typizations = get_first_match(item=item, key_match=SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING, default_return=[])  # TODO: we assume that every part has this aspect!
        cx_id = item.get('catenaXId', '')
        for aspect in part_typizations:
            for localid in aspect['localIdentifiers']:
                if (localid.get('key', '') == 'ManufacturerID') and (localid.get('value', '') == manufacturer):
                    with shelve.open(DB_CX_ITEMS) as db:
                        db[cx_id] = item

# either delete OR create, not both at the same time - for now                
if args.delete:
    delete_assets_from_cx_items()
    delete_registry_entry_from_cx_items()
    delete_db_all(dbname=DB_CX_ITEMS)
else:
    upsert_assets_from_cx_items()
    upsert_registry_entry_from_cx_items(bpn=args.import_for)


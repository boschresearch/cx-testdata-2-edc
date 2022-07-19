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
from dependencies import DB_ID_MAPPINGS, DB_POLICY_ID_MAPPINGS, REGISTRY_BASE_URL, DB_CX_ITEMS, SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING, SCHEMA_TESTDATA_CONTAINER_LOOKUP_STRING, delete_db_all, get_first_match, SCHEMA_AAS_LOOKUP_STRING

def get_testdata_from_file(filename):
    # read the data
    filedata = ''
    with open(filename, 'r', encoding='iso-8859-1') as f:
        filedata = f.read()
    data = json.loads(filedata)

    data = get_first_match(data, key_match=SCHEMA_TESTDATA_CONTAINER_LOOKUP_STRING, default_return=[])
    return data

def get_manufacturers(testdata):
    manufacturers = set()
    for item in testdata:
        part_typizations = get_first_match(item=item, key_match=SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING, default_return=[])
        for aspect in part_typizations:
            for localid in aspect['localIdentifiers']:
                if localid.get('key', '') == 'ManufacturerID':
                    manufacturers.add(localid.get('value', ''))
    return manufacturers

def iterate_bpn_aspects(testdata, bpn):
    """
    Iterate over all aspects / data elements of a given BPN.
    To find out whether an item belongs to the BPN, we look into the SerialPartTypization localIdentifiers.
    Thus, SerialPartTypization aspect must be available.
    """
    for item in testdata:
        part_typizations = get_first_match(item=item, key_match=SCHEMA_SERIAL_PART_TYPIZATION_LOOKUP_STRING, default_return=[])  # TODO: we assume that every part has this aspect!
        cx_id = item.get('catenaXId', '')
        for aspect in part_typizations:
            for localid in aspect['localIdentifiers']:
                if (localid.get('key', '').lower() == 'manufacturerid') and (localid.get('value', '') == bpn):
                    yield item


###################### main ##################
if __name__ == '__main__':
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
    parser.add_argument('--max-counter', default=1000,
            help='Limits number of items to be imported. Reason: 50-Assets-EDC-Bug (each aspect is 1 Asset!). Recommended: 5')


    args = parser.parse_args()
    print(args)

    if not args.input_filename:
        parser.print_help()
        sys.exit(1)

    if not os.path.isfile(args.input_filename):
        print(f"Given input file does not exist: {args.input_filename}", file=sys.stderr)
        sys.exit(1)



    testdata = get_testdata_from_file(filename=args.input_filename)

    if args.list_manufacturers:
        manufacturers = get_manufacturers(testdata)
        print(manufacturers)
        sys.exit(0)


    if args.import_for:
        manufacturer = args.import_for
        db_items = {}

        counter = 0
        counter_max = int(args.max_counter)
        for item in iterate_bpn_aspects(testdata=testdata, bpn=manufacturer):
            # remove unsued aspects to not run over the 50 assets catalog problem
            for x in list(item.keys()):
                if SCHEMA_AAS_LOOKUP_STRING in x:
                    del item[x]
            counter = counter + 1
            if counter > counter_max:
                print(f"counter_max reached. Not adding more items: {counter_max}")
                break
            with shelve.open(DB_CX_ITEMS) as db:
                cx_id = item.get('catenaXId', '')
                db[cx_id] = item
        if counter >= 50:
            print(f"Warning: More than 50 items. Could be a problem with EDC catalog bug that not all assets are found by consumers!")

    # either delete OR create, not both at the same time - for now     
    if args.delete:
        delete_assets_from_cx_items()
        delete_registry_entry_from_cx_items()
        delete_db_all(dbname=DB_CX_ITEMS)
        delete_db_all(dbname=DB_ID_MAPPINGS)
        delete_db_all(dbname=DB_POLICY_ID_MAPPINGS)
    else:
        upsert_assets_from_cx_items()
        upsert_registry_entry_from_cx_items(bpn=args.import_for)




# Copyright (c) 2023 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/boschresearch/cx-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

import requests
from settings import settings
from pycxids.edc.api import EdcProvider

from settings import QUALITY_INVESTIGATION_NOTIFICATION_ASSET_ID

def register_endpoints(edc_data_management_endpoint: str, backend_endpoint_base_url: str, api_key: str):
    """
    Registers the required EDC endpoints

    Currtly only the:
    - qualityinvestigationnotification-receive
    """
    provider = EdcProvider(
        edc_data_managment_base_url=edc_data_management_endpoint,
        auth_key=api_key,
    )

    asset_id = QUALITY_INVESTIGATION_NOTIFICATION_ASSET_ID
    qualityinvestigationnotification_receive_asset_props = {
        "asset:prop:id": asset_id,
        "asset:prop:name": "Asset to receive quality investigations",
        "asset:prop:contenttype": "application/json",
        "asset:prop:notificationtype": "qualityinvestigation",
        "asset:prop:notificationmethod": "receive"
    }

    base_url = f"{backend_endpoint_base_url}/qualityinvestigations/receive"

    asset_created, _, _ = provider.create_asset_and_friends(base_url=base_url, asset_id=asset_id, proxyMethod=True, proxyBody=True,
        asset_additional_props=qualityinvestigationnotification_receive_asset_props)

    if not asset_id == asset_created:
        print(f"Could not create asset: {asset_id} Result: {asset_created} (maybe it already exists? Data address not updated!)")


import requests
from settings import settings
from edc_data_management import EdcDataManagement

def register_endpoints(edc_data_management_endpoint: str, backend_endpoint_base_url: str, auth_key: str='', auth_value: str = ''):
    """
    Registers the required EDC endpoints

    Currtly only the:
    - qualityinvestigationnotification-receive
    """
    edc_mgmt = EdcDataManagement(
        data_management_base_url=edc_data_management_endpoint,
        data_management_auth_key=auth_key,
        data_management_auth_code=auth_value,
    )
    #edc_mgmt.exists(asset_id='')
    qualityinvestigationnotification_receive_asset_props = {
        "asset:prop:id": "qualityinvestigationnotification-receive",
        "asset:prop:name": "Asset to receive quality investigations",
        "asset:prop:contenttype": "application/json",
        "asset:prop:notificationtype": "qualityinvestigation",
        "asset:prop:notificationmethod": "receive"
    }

    qualityinvestigationnotification_receive_data_address_props = {
        "baseUrl": f"{backend_endpoint_base_url}/qualityinvestigations/receive",
        "proxyMethod": True,
        "proxyBody": True,
        #"proxyPath": True,
        "type": "HttpData"
    }

    edc_mgmt.create_asset_by_props(
        asset_props=qualityinvestigationnotification_receive_asset_props,
        data_address_props=qualityinvestigationnotification_receive_data_address_props
    )
    policy_id = edc_mgmt.create_policy(asset_id=qualityinvestigationnotification_receive_asset_props["asset:prop:id"])
    cd_id = edc_mgmt.create_contract_definition(policy_id=policy_id, asset_id=qualityinvestigationnotification_receive_asset_props["asset:prop:id"])

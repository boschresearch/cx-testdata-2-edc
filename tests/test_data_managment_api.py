import os
import requests
import pytest
from uuid import uuid4

PROVIDER_EDC_BASE_URL = os.getenv('PROVIDER_EDC_BASE_URL', 'http://localhost:8080')
PROVIDER_EDC_API_KEY = os.getenv('PROVIDER_EDC_API_KEY', '1234')
NR_OF_ASSETS = int(os.getenv('NR_OF_ASSETS', '10'))

def prepare_data_management_auth():
    return {
        'X-Api-Key': PROVIDER_EDC_API_KEY
    }

def get_number_of_elements(endpoint):
    """
    """
    try:
        r = requests.get(endpoint, headers=prepare_data_management_auth(), params={ 'limit': NR_OF_ASSETS * 2 })
        j = r.json()
        return len(j)
    except Exception as ex:
        print(ex)
        return None


def create_random_asset_and_co(nr_of_assets: int = 1):
    result = []
    for x in range(nr_of_assets):
        asset_id = create_asset()
        policy_id = create_policy(asset_id=asset_id)
        contract_id = create_contract_definition(policy_id=policy_id, asset_id=asset_id)
        created = {
            'asset_id': asset_id, 'policy_id': policy_id, 'contract_id': contract_id
        }
        result.append(created)
    return result

def create_asset():
    asset_id = str(uuid4())
    data = {
        "asset": {
            "properties": {
                "asset:prop:id": asset_id,
                "asset:prop:contenttype": "application/json",
                "asset:prop:policy-id": "use-eu",
            }
        },
        "dataAddress": {
            "properties": {
                "type": "HttpData",
                "endpoint": 'http://localhost'
            }
        }

    }
    r = requests.post(f"{PROVIDER_EDC_BASE_URL}/assets", json=data, headers=prepare_data_management_auth())
    if not r.ok:
        return None
    # TODO: checks
    return asset_id

def create_contract_definition(policy_id: str, asset_id: str):
    cd_id = str(uuid4())
    data = {
        "id": cd_id,
        "accessPolicyId": policy_id,
        "contractPolicyId": policy_id,
        "criteria": [
            {
                "operandLeft": "asset:prop:id",
                "operator": "=",
                "operandRight": asset_id
            }
        ],
    }
    r = requests.post(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions", json=data, headers=prepare_data_management_auth())
    return cd_id

def create_policy(asset_id: str):
    policy_id = str(uuid4())
    data = {
        "id": policy_id,
        "policy": {
            "permissions": [
                {
                    "target": asset_id,
                    "action": {
                        "type": "USE"
                    },
                    "edctype": "dataspaceconnector:permission"
                }
            ],
        },
        "@type": {
            "@policytype": "set"
        }
    }
    r = requests.post(f"{PROVIDER_EDC_BASE_URL}/policydefinitions", json=data, headers=prepare_data_management_auth())
    return policy_id

@pytest.fixture
def edc_is_clean():
    """
    True if assets, policiesand contractdefinitions are empty (or not fetchable)
    """
    nr_of_assets = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/assets")
    nr_of_policies = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/policydefinitions")
    nr_of_contractdefinitions = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions")

    return nr_of_assets == nr_of_policies == nr_of_contractdefinitions == 0

# actual test case
def test_create_and_delete(edc_is_clean: bool):
    """
    This should cover
    - EDC - Test Data Management API - Request all Artefacts
    https://jira.catena-x.net/browse/TEST-24

    - EDC - Test Data Management API - Delete Artefacts
    https://jira.catena-x.net/browse/TEST-25

    - EDC - Test Data Management API - Request non-deleted Artefacts
    https://jira.catena-x.net/browse/TEST-26

    """
    assert edc_is_clean, f"Setup not clean or can not connect. PROVIDER_EDC_BASE_URL: {PROVIDER_EDC_BASE_URL}"
    asset_inf = create_random_asset_and_co(nr_of_assets=NR_OF_ASSETS)
    #assert 'asset_id' in asset_inf
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/assets")
    assert nr_of_elements == NR_OF_ASSETS
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/policydefinitions")
    assert nr_of_elements == NR_OF_ASSETS
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions")
    assert nr_of_elements == NR_OF_ASSETS

    first = asset_inf[0]

    # delete asset
    r = requests.delete(f"{PROVIDER_EDC_BASE_URL}/assets/{first['asset_id']}", headers=prepare_data_management_auth())
    assert str(r.status_code).startswith('20'), f"Response code NOT 20x. status_code: {r.status_code}"
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/assets")
    assert nr_of_elements == NR_OF_ASSETS - 1
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/policydefinitions")
    assert nr_of_elements == NR_OF_ASSETS
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions")
    assert nr_of_elements == NR_OF_ASSETS

    # delete contract definition
    r = requests.delete(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions/{first['contract_id']}", headers=prepare_data_management_auth())
    assert str(r.status_code).startswith('20'), f"Response code NOT 20x. status_code: {r.status_code}"
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions")
    assert nr_of_elements == NR_OF_ASSETS - 1
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/policydefinitions")
    assert nr_of_elements == NR_OF_ASSETS


    # delete policy
    r = requests.delete(f"{PROVIDER_EDC_BASE_URL}/policydefinitions/{first['policy_id']}", headers=prepare_data_management_auth())
    assert str(r.status_code).startswith('20'), f"Response code NOT 20x. status_code: {r.status_code}"
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/policydefinitions")
    assert nr_of_elements == NR_OF_ASSETS - 1

if __name__ == '__main__':
    pytest.main()

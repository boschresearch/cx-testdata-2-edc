import os
import requests
import pytest
from uuid import uuid4

PROVIDER_EDC_BASE_URL = os.getenv('PROVIDER_EDC_BASE_URL', 'http://localhost:8080')
PROVIDER_EDC_API_KEY = os.getenv('PROVIDER_EDC_API_KEY', '1234')


def prepare_data_management_auth():
    return {
        'X-Api-Key': PROVIDER_EDC_API_KEY
    }

def get_number_of_elements(endpoint):
    """
    """
    try:
        r = requests.get(endpoint, headers=prepare_data_management_auth())
        j = r.json()
        return len(j)
    except:
        return None


def create_random_asset_and_co():
    asset_id = create_asset()
    policy_id = create_policy(asset_id=asset_id)
    contract_id = create_contract_definition(policy_id=policy_id)
    return {
        'asset_id': asset_id, 'policy_id': policy_id, 'contract_id': contract_id
    }

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

def create_contract_definition(policy_id: str):
    cd_id = str(uuid4())
    data = {
        "id": cd_id,
        "accessPolicyId": policy_id,
        "contractPolicyId": policy_id,
        "criteria": [],
    }
    r = requests.post(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions", json=data, headers=prepare_data_management_auth())
    return cd_id

def create_policy(asset_id: str):
    policy_id = str(uuid4())
    data = {
        "uid": policy_id,
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
    asset_inf = create_random_asset_and_co()
    assert 'asset_id' in asset_inf
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/assets")
    assert nr_of_elements == 1
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/policydefinitions")
    assert nr_of_elements == 1
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions")
    assert nr_of_elements == 1

    # delete asset
    r = requests.delete(f"{PROVIDER_EDC_BASE_URL}/assets/{asset_inf['asset_id']}", headers=prepare_data_management_auth())
    assert str(r.status_code).startswith('20'), f"Response code NOT 20x. status_code: {r.status_code}"
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/assets")
    assert nr_of_elements == 0
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/policydefinitions")
    assert nr_of_elements == 1
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions")
    assert nr_of_elements == 1

    # delete contract definition
    r = requests.delete(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions/{asset_inf['contract_id']}", headers=prepare_data_management_auth())
    assert str(r.status_code).startswith('20'), f"Response code NOT 20x. status_code: {r.status_code}"
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/contractdefinitions")
    assert nr_of_elements == 0
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/policydefinitions")
    assert nr_of_elements == 1


    # delete policy
    r = requests.delete(f"{PROVIDER_EDC_BASE_URL}/policydefinitions/{asset_inf['policy_id']}", headers=prepare_data_management_auth())
    assert str(r.status_code).startswith('20'), f"Response code NOT 20x. status_code: {r.status_code}"
    nr_of_elements = get_number_of_elements(f"{PROVIDER_EDC_BASE_URL}/policydefinitions")
    assert nr_of_elements == 0

if __name__ == '__main__':
    pytest.main()

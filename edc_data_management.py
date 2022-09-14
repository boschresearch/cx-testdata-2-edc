import requests
from uuid import uuid4

class EdcDataManagement():
    """
    This is a new clean implemenation of what is 'hidden' in edc_handling.
    This implementation does NOT include backward compatibilites prior product-edc 0.1.1.
    """
    def __init__(self,
                data_management_base_url: str,
                data_management_auth_key: str = '',
                data_management_auth_code: str = '',
                backend_auth_code: str = '',
                backend_auth_key: str = 'X-Api-Key',
            ):
        """
        data_management_base_url: base url. /assets /policies etc is added to that
        data_management_auth_key: header key to access data management api
        data_management_auth_code: header value to access data management api

        backend_auth_key: header that is aded to the 'dataAddress' when an asset is created. used to access the backend
        backend_auth_code: value that is added to the 'dataAddress' to access a backend.
        """
        self.data_management_base_url = data_management_base_url
        self.data_management_auth_key = data_management_auth_key
        self.data_management_auth_code = data_management_auth_code
        self.backend_auth_code = backend_auth_code
        self.backend_auth_key = backend_auth_key

    def create_asset_and_friends(self, asset_id: str, endpoint: str):
        asset_id = self.create_asset(asset_id=asset_id, endpoint=endpoint)
        policy_id = self.create_policy(asset_id=asset_id)
        contract_definition_id = self.create_contract_definition(policy_id=policy_id, asset_id=asset_id)
        return {
            'asset_id': asset_id,
            'policy_id': policy_id,
            'contract_definition_id': contract_definition_id,
        }

    def create_asset(self, asset_id: str, endpoint: str):
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
                    "proxyMethod": True,
                    "proxyBody": True,
                    #"proxyPath": False, # to avoid /submodel at the end
                    #"proxyQueryParams": True,
                    "baseUrl": endpoint
                }
            }
        }
        # add secrets for the backen system if set
        if self.backend_auth_code:
            data['dataAddress']['properties']['authCode'] = self.backend_auth_code
            data['dataAddress']['properties']['authKey'] = self.backend_auth_key

        r = requests.post(f"{self.data_management_base_url}/assets", json=data, headers=self._prepare_data_management_auth())
        if not r.ok:
            return None
        # TODO: checks
        return asset_id

    def create_contract_definition(self, policy_id: str, asset_id: str):
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
        r = requests.post(f"{self.data_management_base_url}/contractdefinitions", json=data, headers=self._prepare_data_management_auth())
        return cd_id

    def create_policy(self, asset_id: str):
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
        r = requests.post(f"{self.data_management_base_url}/policydefinitions", json=data, headers=self._prepare_data_management_auth())
        return policy_id

    def _prepare_data_management_auth(self):
        if not self.data_management_auth_key:
            return {}
        headers = {
            self.data_management_auth_key : self.data_management_auth_code
        }
        return headers
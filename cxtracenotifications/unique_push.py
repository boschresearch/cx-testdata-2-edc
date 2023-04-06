# Copyright (c) 2023 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/boschresearch/cx-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0

from uuid import uuid4
from datetime import datetime

import requests
from pycxids.models.generated.assembly_part_relationship import AssemblyPartRelationship, ChildData, QuantityCharacteristic, LifecycleContextCharacteristic
from pycxids.registry.api import CxAas, CxSubmodelEndpoint, CxRegistry
from pycxids.utils.storage import FileStorageEngine
from pycxids.edc.api import EdcConsumer
from pycxids.edc.settings import IDS_PATH
from models_unique_push import UniqueIdPushNotificationReceiveRequestBody, UniqueIdPushNotificationReceiveRequestHeader, UniqueIdPushNotificationReceivePayload, SerializedPartItem, UniqueIdPushClassification

class UniquePushDemo():
    def __init__(self, storage_fn: str, backend_base_url: str,
            our_bpn: str, our_edc_endpoint: str,
            registry_base_url: str, registry_client_id: str, registry_client_secret: str, registry_token_endpoint: str,
            edc_data_managment_base_url: str, edc_auth_key: str, edc_token_receiver_service_base_url: str = None,
        ) -> None:
        #self.storage_fn = storage_fn
        self.storage = FileStorageEngine(storage_fn=self.storage_fn)
        self.backend_base_url = backend_base_url
        # registry information
        self.registry_base_url = registry_base_url
        self.registry_client_id = registry_client_id
        self.registry_client_secret = registry_client_secret
        self.registry_token_endpoint = registry_token_endpoint
        # edc
        self.edc_data_managment_base_url = edc_data_managment_base_url
        self.edc_auth_key = edc_auth_key
        self.edc_token_receiver_service_base_url = edc_token_receiver_service_base_url
        # our org information
        self.our_bpn = our_bpn
        self.our_edc_endpoint = our_edc_endpoint

    def create_twin_and_edc_asset(self, child_cx_id: str, their_edc_endpoint: str, their_bpn: str):
        """
        This is meant for demo purposes only to test the unqiue id push mechanism.

        - Lookup given cx_id (optionally?)
        - Create assemblyPartRelationship with the given cx_id as the only child
        - Create a new twin
        - Create a new EDC asset
        - Push unique ID to the given edc
        """

        now = datetime.now().isoformat(timespec='milliseconds')
        parent_cx_id = str(uuid4())
        aas_id = str(uuid4())
        apr_submodel_id = str(uuid4())
        apr_asset_id = f"{aas_id}-{apr_submodel_id}"

        apr = AssemblyPartRelationship(
            catenaXId=parent_cx_id,
            childParts=[
                ChildData(
                    createdOn=now,
                    lastModifiedOn=now,
                    quantity=QuantityCharacteristic(quantityNumber=1.0),
                    lifecycleContext=LifecycleContextCharacteristic.as_built,
                    childCatenaXId=child_cx_id,
                )
            ]
        )
        # store the apr for later requests
        apr_dict = apr.dict()
        self.storage.put(key=apr_asset_id, value=apr_dict)

        # create registry entry
        ep_address = f"{self.backend_base_url}/{apr_asset_id}"
        aas = CxAas(
            submodels=[
                CxSubmodelEndpoint(
                    endpointAddress=ep_address,
                    semantic_id='urn:bamm:io.catenax.assembly_part_relationship:1.1.1#AssemblyPartRelationship', # TODO
                    identification=apr_submodel_id,
                    idShort='assemblyPartRelationship',
                )
            ],
            identification=aas_id,
            cxid=parent_cx_id,
        )
        registry = CxRegistry(base_url=self.registry_base_url, client_id=self.registry_client_id, client_secret=self.registry_client_secret, token_url=self.registry_token_endpoint)
        aas_created = registry.create(aas=aas)

        # and push it to the other organization
        #portal = Portal(portal_base_url=self.portal_base_url, client_id=self.portal_client_id, client_secret=self.portal_client_secret, token_url=self.portal_token_endpoint)
        #portal.discover_edc_endpoint()
        # we don't need EDC discovery since we get the endpoint from the id push message
        ASSET_ID_PUSH_UNIQUE_ID = 'uniqueidpushnnotification-receipt'
        consumer = EdcConsumer(edc_data_managment_base_url=self.edc_data_managment_base_url, auth_key=self.edc_auth_key, token_receiver_service_base_url=self.edc_token_receiver_service_base_url)
        if not IDS_PATH in their_edc_endpoint:
            their_edc_endpoint = their_edc_endpoint + IDS_PATH
        agreement_id = consumer.negotiate_and_transfer(asset_id=ASSET_ID_PUSH_UNIQUE_ID, provider_ids_endpoint=their_edc_endpoint)
        # TODO: cache agreement_id
        provider_edr = consumer.transfer_and_wait_provider_edr(provider_ids_endpoint=their_edc_endpoint, asset_id=ASSET_ID_PUSH_UNIQUE_ID)

        serial_part_item = SerializedPartItem(
            manufacturerId=self.our_bpn,
            catenaxId=parent_cx_id,
            partInstanceId=parent_cx_id, # in our case we don't have a separate local serial number
            manufacturerPartId='GEN-PartXXX',
            customerPartId='GEN-PartXXX',
        )

        msg = UniqueIdPushNotificationReceiveRequestBody(
            header=UniqueIdPushNotificationReceiveRequestHeader(
                classification=UniqueIdPushClassification.Child_Relationship,
                notificationId=str(uuid4()),
                senderBPN=self.our_bpn,
                senderAddress=self.our_edc_endpoint,
                recipientBPN=their_bpn,
            ),
            content=UniqueIdPushNotificationReceivePayload(
                listOfItems=[
                    serial_part_item
                ],
                information="This is a newly produced part."
            )
        )
        msg_dict = msg.dict()

        # and now, finally push the information
        url = provider_edr.get('baseUrl', None)
        if not url:
            pass # TODO:
        r = requests.post(url=url, data=msg_dict, headers={'Authorization': provider_edr['authCode']})
        if not r.ok:
            print(f"{r.status_code} - {r.reason} - {r.content}")
            return None
        return parent_cx_id

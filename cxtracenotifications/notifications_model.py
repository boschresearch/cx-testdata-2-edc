# generated by datamodel-codegen:
#   filename:  quality-notification-cx-release-2-PI4-openapi.yaml
#   timestamp: 2022-11-14T10:04:33+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field, constr

from pycxids.models.base_model import MyBaseModel

class QualityNotificationGetRequestHeader(MyBaseModel):
    notificationId: str = Field(
        ...,
        description='A UUIDv4 to uniquely identify a quality notification.',
        example='a7954026-3aff-4b6c-92bf-04671ef2fa46',
    )
    senderBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the sender. Actually, this value is not used to resolve the quality notification. Rather, it is used to do a plausibility check.',
        example='BPNL00000003BW3S',
    )
    senderAddress: AnyUrl = Field(
        ...,
        description='The Eclipse Dataspace Connector (EDC) URL of the sender. Actually, this value is not used to resolve the quality notification. Rather, it is used to do a plausibility check.',
        example='https://edc.company-xyz.io/BPNL00000003BW3S',
    )
    recipientBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the receiver. Actually, this value is not used to resolve the quality notification. Rather, it is used to do a plausibility check.',
        example='BPNL00000003BV4H',
    )


class QualityNotificationReceivePayload(MyBaseModel):
    information: Optional[constr(max_length=1000)] = Field(
        None, example='Gear boxes loose oil while driving.'
    )
    listOfAffectedItems: List[str] = Field(
        ...,
        example=[
            'urn:uuid:57e4e3c1-a6f0-46a0-90df-1fb17cbc157d',
            'urn:uuid:e4da568b-8cf1-4f5f-a96a-cf26265b2c72',
        ],
    )


class QualityNotificationUpdatePayload(MyBaseModel):
    information: Optional[constr(max_length=1000)] = Field(
        None, example='Gear boxes loose oil while driving.'
    )


class QualityClassification(Enum):
    QM_Investigation = 'QM-Investigation'
    QM_Alert = 'QM-Alert'


class QualitySeverity(Enum):
    MINOR = 'MINOR'
    MAJOR = 'MAJOR'
    CRITICAL = 'CRITICAL'
    LIFE_THREATENING = 'LIFE-THREATENING'


class QualityStatus(Enum):
    CREATED = 'CREATED'
    SENT = 'SENT'
    RECEIVED = 'RECEIVED'
    ACKNOWLEDGED = 'ACKNOWLEDGED'
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    CLOSED = 'CLOSED'


class QualityNotificationReceiveRequestHeader(MyBaseModel):
    notificationId: str = Field(
        ...,
        description='A UUIDv4 to uniquely identify a quality notification.',
        example='a7954026-3aff-4b6c-92bf-04671ef2fa46',
    )
    senderBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the sender.',
        example='BPNL00000003BW3S',
    )
    senderAddress: AnyUrl = Field(
        ...,
        description='The Eclipse Dataspace Connector (EDC) URL of the sender.',
        example='https://edc.company-xyz.io/BPNL00000003BW3S',
    )
    recipientBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the receiver.',
        example='BPNL00000003BV4H',
    )
    classification: QualityClassification
    severity: QualitySeverity
    relatedNotificationId: Optional[str] = Field(
        None,
        description='A UUIDv4 to uniquely identify a related quality notification.',
        example='7895a39d-c4ef-4b75-b39f-cae8207a262f',
    )
    status: Optional[QualityStatus] = None
    targetDate: Optional[datetime] = Field(
        None,
        description='The date and time when a processing of the notification is expected by the sender.',
        example='2022-07-28T14:41:13.214Z',
    )


class QualityNotificationGetResponseHeader(MyBaseModel):
    notificationId: str = Field(
        ...,
        description='A UUIDv4 to uniquely identify a quality notification.',
        example='a7954026-3aff-4b6c-92bf-04671ef2fa46',
    )
    senderBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the sender.',
        example='BPNL00000003BW3S',
    )
    senderAddress: AnyUrl = Field(
        ...,
        description='The Eclipse Dataspace Connector (EDC) URL of the sender.',
        example='https://edc.company-xyz.io/BPNL00000003BW3S',
    )
    recipientBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the receiver.',
        example='BPNL00000003BV4H',
    )
    severity: QualitySeverity
    status: Optional[QualityStatus] = None
    targetDate: Optional[datetime] = Field(
        None,
        description='The date and time when a processing of the notification is expected by the sender.',
        example='2022-07-28T14:41:13.214Z',
    )


class QualityNotificationUpdateRequestHeader(MyBaseModel):
    notificationId: str = Field(
        ...,
        description='A UUIDv4 to uniquely identify a quality notification. Actually, this value cannot be updated. Rather, it is used to do a plausibility check.',
        example='a7954026-3aff-4b6c-92bf-04671ef2fa46',
    )
    senderBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the sender. Actually, this value cannot be updated. Rather, it is used to do a plausibility check.',
        example='BPNL00000003BW3S',
    )
    senderAddress: AnyUrl = Field(
        ...,
        description='The Eclipse Dataspace Connector (EDC) URL of the sender. Actually, this value cannot be updated. Rather, it is used to do a plausibility check.',
        example='https://edc.company-xyz.io/BPNL00000003BW3S',
    )
    recipientBPN: str = Field(
        ...,
        description='The business partner number (BPN) of the receiver. Actually, this value cannot be updated. Rather, it is used to do a plausibility check.',
        example='BPNL00000003BV4H',
    )
    severity: Optional[QualitySeverity] = None
    status: Optional[QualityStatus] = None
    targetDate: Optional[datetime] = Field(
        None,
        description='The date and time when a processing of the notification is expected by the sender.',
        example='2022-07-28T14:41:13.214Z',
    )


class QualityNotificationReceiveRequestBody(MyBaseModel):
    header: QualityNotificationReceiveRequestHeader
    content: QualityNotificationReceivePayload


class QualityNotificationUpdateRequestBody(MyBaseModel):
    header: QualityNotificationUpdateRequestHeader
    content: Optional[QualityNotificationUpdatePayload] = None

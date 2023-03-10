# coding: utf-8

from __future__ import annotations
from datetime import date, datetime  # noqa: F401

import re  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from .base_model import MyBaseModel
from pydantic import AnyUrl, EmailStr, validator  # noqa: F401


class AdministrativeInformation(MyBaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    AdministrativeInformation - a model defined in OpenAPI

        revision: The revision of this AdministrativeInformation [Optional].
        version: The version of this AdministrativeInformation [Optional].
    """

    revision: Optional[str] = None
    version: Optional[str] = None

AdministrativeInformation.update_forward_refs()

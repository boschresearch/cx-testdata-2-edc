# Copyright (c) 2023 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/boschresearch/cx-testdata-2-edc
#
# SPDX-License-Identifier: Apache-2.0


class MyBaseModel(BaseModel):
    def dict(self, exclude_none=True, **kwargs):
        # no config class option for this. needs to be manually changed
        return super().dict(exclude_none=exclude_none, **kwargs)
    def json(self, exclude_none=True, **kwargs):
        result = super().dict(exclude_none=exclude_none, **kwargs)
        json_result = jsonable_encoder(result) # converts e.g. datetime to string
        return json_result


    class Config:
        allow_population_by_field_name = True
        use_enum_values = True

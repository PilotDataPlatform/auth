# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pydantic import BaseModel, Field, validator

from app.models.api_response import EAPIResponseCode
from app.models.base_models import APIResponse
from app.resources.error_handler import APIException


class InvitationPUT(BaseModel):
    status: str = ""

    @validator('status')
    def validate_status(cls, v):
        if v not in ['complete', 'pending']:
            raise APIException(status_code=EAPIResponseCode.bad_request.value, error_msg='Invalid status')
        return v

class InvitationListPOST(BaseModel):
    page: int = 0
    page_size: int = 25
    order_by: str = 'create_timestamp'
    order_type: str = 'asc'
    filters: dict = {}


class InvitationPOST(BaseModel):
    email: str
    platform_role: str
    relationship: dict = {}
    invited_by: str

    @validator('relationship')
    def validate_relationship(cls, v):
        if not v:
            return v
        for key in ['project_geid', 'project_role', 'inviter']:
            if key not in v.keys():
                raise APIException(
                    status_code=EAPIResponseCode.bad_request.value,
                    error_msg=f'relationship missing required value {key}',
                )
        return v

    @validator('platform_role')
    def validate_platform_role(cls, v):
        if v not in ['admin', 'member']:
            raise APIException(status_code=EAPIResponseCode.bad_request.value, error_msg='Invalid platform_role')
        return v


class InvitationPOSTResponse(APIResponse):
    result: dict = Field(
        {},
        example={},
    )

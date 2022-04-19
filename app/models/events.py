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

import json
from pydantic import BaseModel, Field, validator

from app.models.api_response import EAPIResponseCode
from app.models.base_models import APIResponse
from app.resources.error_handler import APIException
from app.models.sql_events import UserEventModel


class EventPOST(BaseModel):
    target_user_id: str = ""
    target_user: str = ""
    operator_id: str = ""
    operator: str
    event_type: str
    detail: dict = {}

    @validator('event_type')
    def validate_event_type(cls, v):
        valid_event_types = [
            'INVITE_TO_PLATFORM',
            'INVITE_TO_PROJECT',
            'REMOVE_FROM_PROJECT',
            'ROLE_CHANGE',
            'ACCOUNT_DISABLE',
            'ACCOUNT_ACTIVATED',
        ]
        if v not in valid_event_types:
            raise APIException(status_code=EAPIResponseCode.bad_request.value, error_msg='Invalid event_type')
        return v


class EventPOSTResponse(APIResponse):
    result: dict = Field(
        {},
        example={},
    )


class EventGETResponse(APIResponse):
    result: dict = Field(
        {},
        example={
           "code": 200,
           "error_msg": "",
           "num_of_pages": 2,
           "page": 0,
           "result": [
              {
                 "detail": {
                    "from": "contributor",
                    "project_code": "indoctestproject",
                    "to": "contributor"
                 },
                 "event_type": "ROLE_CHANGE",
                 "id": "eb28391b-7eb5-4373-b36f-2c919295763c",
                 "operator": "admin",
                 "operator_id": "eef51a4b-d8ac-4526-8811-1d5fc1aaa998",
                 "target_user": "exampleuser",
                 "target_user_id": "18ab20c1-173d-404a-826c-af619cd7a1ed",
                 "timestamp": "2022-04-07 18:38:41.891580"
              },
              {
                 "detail": {
                    "invitation_id": "5afdae38-c4d4-4d84-812e-918b7ae5ce0a",
                    "platform_role": "admin"
                 },
                 "event_type": "INVITE_TO_PLATFORM",
                 "id": "ce395904-d4a2-43a4-8704-4b8f001b4743",
                 "operator": "admin",
                 "operator_id": "eef51a4b-d8ac-4526-8811-1d5fc1aaa998",
                 "target_user": "exampleuser",
                 "target_user_id": "18ab20c1-173d-404a-826c-af619cd7a1ed",
                 "timestamp": "2022-04-06 14:06:48.474718"
              },
              {
                 "detail": {},
                 "event_type": "ACCOUNT_ACTIVATED",
                 "id": "b63a1c33-2523-45ba-9881-4a9cc07e2001",
                 "operator": "admin",
                 "operator_id": "eef51a4b-d8ac-4526-8811-1d5fc1aaa998",
                 "target_user": "exampleuser",
                 "target_user_id": "18ab20c1-173d-404a-826c-af619cd7a1ed",
                 "timestamp": "2022-04-06 13:59:29.574938"
              },
              {
                 "detail": {},
                 "event_type": "ACCOUNT_DISABLE",
                 "id": "7b5b9212-a55d-4d18-988c-d2729a610931",
                 "operator": "admin",
                 "operator_id": "eef51a4b-d8ac-4526-8811-1d5fc1aaa998",
                 "target_user": "exampleuser",
                 "target_user_id": "18ab20c1-173d-404a-826c-af619cd7a1ed",
                 "timestamp": "2022-04-06 13:59:16.828590"
              }
           ],
           "total": 7
        }
    )


class EventList(BaseModel):
    page: int = 0
    page_size: int = 25
    order_by: str = "timestamp"
    order_type: str = "asc"
    project_code: str = ""
    user_id: str = ""
    invitation_id: str = ""

    @validator('order_type')
    def validate_order_type(cls, v):
        if v not in ['asc', 'desc']:
            raise APIException(status_code=EAPIResponseCode.bad_request.value, error_msg='Invalid order_type')
        return v

    @validator('order_by')
    def validate_order_by(cls, v):
        fields = ['id', 'target_user', 'operator', 'event_type', 'timestamp']
        if v not in fields:
            raise APIException(status_code=EAPIResponseCode.bad_request.value, error_msg='Invalid order_by')
        return v

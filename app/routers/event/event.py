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

from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db
from fastapi_utils.cbv import cbv
from common import LoggerFactory
import math

from app.commons.psql_services.user_event import create_event, query_events
from app.config import ConfigSettings
from app.models.api_response import APIResponse, EAPIResponseCode
from app.models.events import EventPOST, EventPOSTResponse, EventGETResponse, EventList
from app.resources.keycloak_api.ops_admin import OperationsAdmin

router = APIRouter()

_API_TAG = 'Event'


@cbv(router)
class UserEvent:
    _logger = LoggerFactory('api_user_event').get_logger()

    @router.post(
        '/events',
        response_model=EventPOSTResponse,
        summary='Creates a new event',
        tags=[_API_TAG]
    )
    def create_event(self, data: EventPOST):
        """
            Create event in psql event table of actions on user account such as invites or roles changes.
        """
        self._logger.info('Called create_event')
        api_response = APIResponse()

        event_data = {
            "operator_id": data.operator_id,
            "operator": data.operator,
            "target_user_id": data.target_user_id,
            "target_user": data.target_user,
            "event_type": data.event_type,
            "detail": data.detail,
        }
        event_obj = create_event(event_data)
        api_response.result = event_obj.to_dict()
        return api_response.json_response()


    @router.get(
        '/events',
        response_model=EventGETResponse,
        summary='list events',
        tags=[_API_TAG]
    )
    def list_events(self, data: EventList = Depends(EventList)):
        """
            Lists events from psql event table of actions on user account such as invites or roles changes.
        """
        self._logger.info('Called list_events')
        api_response = APIResponse()
        query = {}
        if data.user_id:
            query["target_user_id"] = data.user_id
        if data.project_code:
            query["project_code"] = data.project_code
        if data.invitation_id:
            query["invitation_id"] = data.invitation_id
        event_list, total = query_events(query, data.page, data.page_size, data.order_type, data.order_by)
        api_response.page = data.page
        api_response.total = total
        api_response.num_of_pages = math.ceil(total / data.page_size)
        api_response.result = [i.to_dict() for i in event_list]
        return api_response.json_response()

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

from fastapi_sqlalchemy import db
from common import LoggerFactory
from typing import Tuple

from app.models.api_response import EAPIResponseCode
from app.models.sql_events import UserEventModel
from app.resources.error_handler import APIException
from app.resources.keycloak_api.ops_admin import OperationsAdmin
from app.config import ConfigSettings
from sqlalchemy import cast, String, or_


_logger = LoggerFactory('api_user_event').get_logger()


def query_events(query: dict, page: int, page_size: int, order_type: str, order_by: str) -> Tuple[list, int]:
    try:
        filters = {}
        event_query = db.session.query(UserEventModel)
        for key, value in query.items():
            if key == "project_code":
                event_query = event_query.filter(
                    or_(
                        UserEventModel.detail['project_code'].as_string() == value,
                        UserEventModel.event_type.in_(["ACCOUNT_DISABLE", "ACCOUNT_ACTIVATED"])
                    )
                )
            elif key == "invitation_id":
                event_query = event_query.filter(UserEventModel.detail['invitation_id'].as_string() == value)
            else:
                event_query = event_query.filter(getattr(UserEventModel, key) == value)
        if order_type == "desc":
            order_by = getattr(UserEventModel, order_by).desc()
        else:
            order_by = getattr(UserEventModel, order_by).asc()
        event_query = event_query.order_by(order_by)
        total = event_query.count()
        event_query = event_query.limit(page_size).offset(page * page_size)
        events = event_query.all()
    except Exception as e:
        error_msg = f'Error querying events in psql: {str(e)}'
        _logger.error(error_msg)
        raise APIException(status_code=EAPIResponseCode.internal_error.value, error_msg=error_msg)
    return events, total


def create_event(model_data: dict) -> UserEventModel:
    if not model_data.get("operator_id") and model_data.get("operator"):
        admin_client = OperationsAdmin(ConfigSettings.KEYCLOAK_REALM)
        model_data["operator_id"] = str(admin_client.get_user_by_username(model_data["operator"])["id"])
    if not model_data.get("target_user_id") and model_data.get("target_user"):
        admin_client = OperationsAdmin(ConfigSettings.KEYCLOAK_REALM)
        model_data["target_user_id"] = str(admin_client.get_user_by_username(model_data["target_user"])["id"])

    # remove blank items
    model_data = {k: v for k, v in model_data.items() if v}

    if not model_data.get("operator_id"):
        model_data["operator_id"] = None

    try:
        event = UserEventModel(**model_data)
        db.session.add(event)
        db.session.commit()
    except Exception as e:
        error_msg = f'Error creating event in psql: {str(e)}'
        _logger.error(error_msg)
        raise APIException(status_code=EAPIResponseCode.internal_error.value, error_msg=error_msg)
    return event


def update_event(query: dict, update_data: dict) -> dict:
    filters = {}
    event_query = db.session.query(UserEventModel)
    for key, value in query.items():
        if key == "invitation_id":
            event_query = event_query.filter(UserEventModel.detail['invitation_id'].as_string() == value)
        else:
            event_query = event_query.filter(getattr(UserEventModel, key) == value)
    event = event_query.first()
    if not event:
        error_msg = f'Event not found with query: {query}'
        _logger.error(error_msg)
        raise APIException(status_code=EAPIResponseCode.internal_error.value, error_msg=error_msg)

    for key, value in update_data.items():
        setattr(event, key, value)
    db.session.commit()
    return event

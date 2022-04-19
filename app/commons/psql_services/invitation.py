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

from app.models.api_response import EAPIResponseCode
from app.models.sql_invitation import InvitationModel
from app.resources.error_handler import APIException

_logger = LoggerFactory('api_invitation').get_logger()


def query_invites(query: dict) -> list:
    try:
        invites = db.session.query(InvitationModel).filter_by(**query).all()
    except Exception as e:
        error_msg = f'Error querying invite in psql: {str(e)}'
        _logger.error(error_msg)
        raise APIException(status_code=EAPIResponseCode.internal_error.value, error_msg=error_msg)
    return invites


def create_invite(model_data: dict) -> InvitationModel:
    try:
        invitation_entry = InvitationModel(**model_data)
        db.session.add(invitation_entry)
        db.session.commit()
        return invitation_entry
    except Exception as e:
        error_msg = f'Error creating invite in psql: {str(e)}'
        _logger.error(error_msg)
        raise APIException(status_code=EAPIResponseCode.internal_error.value, error_msg=error_msg)

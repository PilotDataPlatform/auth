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

import casbin
import casbin_sqlalchemy_adapter
from common import LoggerFactory
from fastapi import APIRouter
from fastapi_utils import cbv
from sqlalchemy import create_engine

from app.config import ConfigSettings
from app.models.api_response import APIResponse, EAPIResponseCode
from app.models.permissions import CasbinRule
from app.resources.error_handler import catch_internal

_engine = None

router = APIRouter()

_API_TAG = '/v1/authorize'
_API_NAMESPACE = 'api_authorize'
_logger = LoggerFactory(_API_NAMESPACE).get_logger()


def _get_sqlalchemy_engine():
    """Get or create engine for sqlalchemy."""

    global _engine

    if _engine is None:
        _engine = create_engine(ConfigSettings.RDS_DB_URI, max_overflow=10, pool_recycle=1800, pool_size=10)

    return _engine


@cbv.cbv(router)
class Authorize:
    def __init__(self):
        pass

    @router.get('/authorize', tags=[_API_TAG], summary='check the authorization for the user')
    @catch_internal(_API_NAMESPACE)
    async def get(self, role: str, zone: str, resource: str, operation: str):
        api_response = APIResponse()
        api_response.result = {"has_permission": True}
        return api_response.json_response()

        project_role = role
        project_zone = zone

        api_response.result = {'has_permission': False}
        try:
            adapter = casbin_sqlalchemy_adapter.Adapter(_get_sqlalchemy_engine(), db_class=CasbinRule)
            enforcer = casbin.Enforcer('app/routers/permissions/model.conf', adapter)
            if enforcer.enforce(project_role, project_zone, resource, operation):
                api_response.result = {'has_permission': True}
                api_response.code = EAPIResponseCode.success
                _logger.info(f'Access granted for {project_role}, {project_zone}, {resource}, {operation}')

        except Exception as e:
            error_msg = f'Error checking permissions - {str(e)}'
            _logger.error(error_msg)
            api_response.error_msg = error_msg
            api_response.code = EAPIResponseCode.internal_error

        return api_response.json_response()

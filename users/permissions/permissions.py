import casbin
import casbin_sqlalchemy_adapter
from common.services.logger_services.logger_factory_service import SrvLoggerFactory
from flask import request
from flask_restx import Resource
from sqlalchemy import create_engine

from config import ConfigSettings
from models.api_response import APIResponse
from models.api_response import EAPIResponseCode
from users import api

_logger = SrvLoggerFactory('api_authorize').get_logger()

_engine = None


def _get_sqlalchemy_engine():
    """Get or create engine for sqlalchemy."""

    global _engine

    if _engine is None:
        _engine = create_engine(ConfigSettings.RDS_DB_URI, max_overflow=10, pool_recycle=1800, pool_size=10)

    return _engine


class Authorize(Resource):
    def get(self):
        api.logger.info('Calling CheckPermissions get')
        api_response = APIResponse()
        data = request.args
        project_role = data.get("role")
        project_zone = data.get("zone")
        resource = data.get("resource")
        operation = data.get("operation")
        if not project_role or not project_zone or not resource or not operation:
            _logger.info('Missing required paramter')
            api_response.set_error_msg("Missing required parameters")
            api_response.set_code(EAPIResponseCode.bad_request)
            return api_response.to_dict(), api_response.code

        api_response.set_result({"has_permission": False})
        try:
            adapter = casbin_sqlalchemy_adapter.Adapter(_get_sqlalchemy_engine())
            enforcer = casbin.Enforcer("users/permissions/model.conf", adapter)
            if enforcer.enforce(project_role, project_zone, resource, operation):
                api_response.set_result({"has_permission": True})
                api_response.set_code(EAPIResponseCode.success)
                _logger.info(f'Access granted for {project_role}, {project_zone}, {resource}, {operation}')
        except Exception as e:
            error_msg = f"Error checking permissions - {str(e)}"
            _logger.error(error_msg)
            api_response.set_error_msg(error_msg)
            api_response.set_code(EAPIResponseCode.internal_error)
        return api_response.to_dict(), api_response.code

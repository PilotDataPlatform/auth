from fastapi import APIRouter
from fastapi.responses import Response
from fastapi_utils import cbv
from fastapi_sqlalchemy import db
from app.models.sql_events import UserEventModel
from app.models.sql_invitation import InvitationModel
from sqlalchemy import create_engine
from app.resources.error_handler import APIException
from app.config import ConfigSettings
from common import LoggerFactory


logger = LoggerFactory('api_health').get_logger()

router = APIRouter(tags=["Health"])


def psql_health_check() -> bool:
    try:
        create_engine(ConfigSettings.RDS_DB_URI, echo=True)
    except Exception as e:
        error_msg = f"Couldn't connect to postgres: {e}"
        logger.error(error_msg)
        raise APIException(error_msg=error_msg, status_code=503)

    try:
        db.session.query(UserEventModel).first()
    except Exception as e:
        error_msg = f"Couldn't query user_event table: {e}"
        logger.error(error_msg)
        raise APIException(error_msg=error_msg, status_code=503)
    try:
        db.session.query(InvitationModel).first()
    except Exception as e:
        error_msg = f"Couldn't query invitation table: {e}"
        logger.error(error_msg)
        raise APIException(error_msg=error_msg, status_code=503)
    return True


@cbv.cbv(router)
class Health:
    @router.get(
        '/health',
        summary="Health check",
    )
    async def get(self):
        logger.info("Starting health checks")
        psql_health_check()
        return Response(status_code=204)

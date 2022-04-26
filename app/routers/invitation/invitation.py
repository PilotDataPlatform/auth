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

import math

from fastapi import APIRouter
from fastapi_sqlalchemy import db
from fastapi_utils.cbv import cbv
from common import LoggerFactory

from app.commons.project_services import get_project_by_geid, get_project_by_code
from app.commons.psql_services.invitation import create_invite, query_invites
from app.commons.psql_services.user_event import create_event, update_event
from app.config import ConfigSettings
from app.models.api_response import APIResponse, EAPIResponseCode
from app.models.invitation import (
    InvitationListPOST,
    InvitationPOST,
    InvitationPOSTResponse,
    InvitationPUT,
)
from app.models.sql_invitation import InvitationModel
from app.resources.error_handler import APIException
from app.resources.keycloak_api.ops_admin import OperationsAdmin
from app.routers.invitation.invitation_notify import send_emails
from app.services.data_providers.ldap_client import LdapClient

router = APIRouter()

_API_TAG = 'Invitation'


@cbv(router)
class Invitation:
    _logger = LoggerFactory('api_invitation').get_logger()

    @router.post(
        '/invitations',
        response_model=InvitationPOSTResponse,
        summary='Creates an new invitation',
        tags=[_API_TAG]
    )
    def create_invitation(self, data: InvitationPOST):
        self._logger.info('Called create_invitation')
        res = APIResponse()
        email = data.email
        platform_role = data.platform_role
        relation_data = data.relationship
        project_role = relation_data.get('project_role')

        project = None
        if relation_data:
            if relation_data.get('project_geid'):
                project = get_project_by_geid(relation_data.get('project_geid'))
            elif relation_data.get('project_code'):
                project = get_project_by_code(relation_data.get('project_code'))
            query = {'project_code': project['code'], 'email': email}
            if query_invites(query):
                res.result = 'Invitation for this user already exists'
                res.code = EAPIResponseCode.conflict
                return res.json_response()

        admin_client = OperationsAdmin(ConfigSettings.KEYCLOAK_REALM)
        if admin_client.get_user_by_email(email):
            self._logger.info('User already exists in platform')
            res.result = '[ERROR] User already exists in platform'
            res.code = EAPIResponseCode.bad_request
            return res.json_response()

        account_in_ad = False
        if ConfigSettings.ENABLE_ACTIVE_DIRECTORY:
            ldap_cli = LdapClient()
            account_in_ad = ldap_cli.is_account_in_ad(email)
            if account_in_ad:
                group_dn = ldap_cli.format_group_dn(ConfigSettings.AD_USER_GROUP)
                user_dn, _ = ldap_cli.get_user_by_email(email)
                ldap_cli.add_user_to_group(user_dn, group_dn)
                if platform_role == 'admin':
                    group_dn = ldap_cli.format_group_dn(ConfigSettings.AD_ADMIN_GROUP)
                    ldap_cli.add_user_to_group(user_dn, group_dn)
                elif relation_data:
                    group_dn = ldap_cli.format_group_dn(project['code'])
                    ldap_cli.add_user_to_group(user_dn, group_dn)

        model_data = {
            'email': email,
            'invited_by': data.invited_by,
            'project_role': project_role,
            'platform_role': platform_role,
            'status': 'pending',
        }
        if project:
            model_data['project_code'] = project['code']
        invitation_entry = create_invite(model_data)

        event_detail = {
            "operator": invitation_entry.invited_by,
            "event_type": "INVITE_TO_PROJECT" if invitation_entry.project_code else "INVITE_TO_PLATFORM",
            "detail": {
                "invitation_id": str(invitation_entry.id),
                "platform_role": invitation_entry.platform_role,
            }
        }
        if project:
            event_detail["detail"]["project_role"] = invitation_entry.project_role
            event_detail["detail"]["project_code"] = project["code"]
        create_event(event_detail)
        send_emails(invitation_entry, project, account_in_ad)
        res.result = 'success'
        return res.json_response()

    @router.get(
        '/invitation/check/{email}',
        response_model=InvitationPOSTResponse,
        summary="This method allow to get user's detail on the platform.",
        tags=[_API_TAG]
    )
    def check_user(self, email: str, project_code: str = ''):
        self._logger.info('Called check_user')
        res = APIResponse()
        admin_client = OperationsAdmin(ConfigSettings.KEYCLOAK_REALM)
        user_info = admin_client.get_user_by_email(email)
        project = None
        if not user_info:
            invite = db.session.query(InvitationModel).filter_by(email=email, status="pending").first()
            if invite:
                res.result = {
                    'name': '',
                    'email': invite.email,
                    'status': 'invited',
                    'role': invite.platform_role,
                    'relationship': {},
                }
                return res.json_response()
            raise APIException(status_code=EAPIResponseCode.not_found.value, error_msg='User not found in keycloak')
        if project_code:
            project = get_project_by_code(project_code)

        roles = admin_client.get_user_realm_roles(user_info['id'])
        platform_role = 'member'
        project_role = ''
        for role in roles:
            if 'platform-admin' == role['name']:
                platform_role = 'admin'
            if project and project['code'] == role['name'].split('-')[0]:
                project_role = role['name'].split('-')[1]
        res.result = {
            'name': user_info['username'],
            'email': user_info['email'],
            'status': user_info['attributes'].get('status', ['pending'])[0],
            'role': platform_role,
            'relationship': {},
        }
        if project and project_role:
            res.result['relationship'] = {
                'project_code': project['code'],
                'project_role': project_role,
            }
        return res.json_response()

    @router.post(
        '/invitation-list',
        response_model=InvitationPOSTResponse,
        summary='list invitations from psql',
        tags=[_API_TAG]
    )
    def invitation_list(self, data: InvitationListPOST):
        self._logger.info('Called invitation_list')
        res = APIResponse()
        query = {}
        for field in ['project_code', 'status']:
            if data.filters.get(field):
                query[field] = data.filters[field]
        try:
            invites = db.session.query(InvitationModel).filter_by(**query)
            for field in ['email', 'invited_by']:
                if data.filters.get(field):
                    invites = invites.filter(getattr(InvitationModel, field).like('%' + data.filters[field] + '%'))
            if data.order_type == 'desc':
                sort_param = getattr(InvitationModel, data.order_by).desc()
            else:
                sort_param = getattr(InvitationModel, data.order_by).asc()
            count = invites.count()
            invites = invites.order_by(sort_param).offset(data.page * data.page_size).limit(data.page_size).all()
        except Exception as e:
            error_msg = f'Error querying invite for listing in psql: {str(e)}'
            self._logger.error(error_msg)
            raise APIException(status_code=EAPIResponseCode.internal_error.value, error_msg=error_msg)

        res.result = [i.to_dict() for i in invites]
        res.page = data.page
        res.num_of_pages = math.ceil(count / data.page_size)
        res.total = count
        return res.json_response()

    @router.put(
        '/invitation/{invite_id}',
        response_model=InvitationPOSTResponse,
        summary='update a single invite',
        tags=[_API_TAG]
    )
    def invitation_update(self, invite_id: str, data: InvitationPUT):
        self._logger.info('Called invitation_update')
        res = APIResponse()
        update_data = {}
        if data.status:
            update_data["status"] = data.status

        query = {"id": invite_id}
        if data.status == "complete":
            # update user event entry to add the target_user
            invite = db.session.query(InvitationModel).filter_by(**query).first()
            admin_client = OperationsAdmin(ConfigSettings.KEYCLOAK_REALM)
            user = admin_client.get_user_by_email(invite.email)
            update_event({"invitation_id": invite_id}, {"target_user": user["username"], "target_user_id": user["id"]})
        try:
            db.session.query(InvitationModel).filter_by(**query).update(update_data)
            db.session.commit()
        except Exception as e:
            error_msg = f'Error updating invite in psql: {str(e)}'
            self._logger.error(error_msg)
            raise APIException(status_code=EAPIResponseCode.internal_error.value, error_msg=error_msg)
        res.result = "success"
        return res.json_response()

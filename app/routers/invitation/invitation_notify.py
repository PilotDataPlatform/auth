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

import base64

from common import LoggerFactory

from app.config import ConfigSettings
from app.models.sql_invitation import InvitationModel
from app.resources.keycloak_api.ops_admin import OperationsAdmin
from app.services.notifier_services.email_service import SrvEmail

_logger = LoggerFactory('api_invitation').get_logger()


def send_emails(invitation_entry: InvitationModel, project: dict, account_in_ad: bool):
    _logger.info('Called send_emails')
    email_sender = SrvEmail()

    admin_client = OperationsAdmin(ConfigSettings.KEYCLOAK_REALM)
    inviter_entry = admin_client.get_user_by_username(invitation_entry.invited_by)

    template_kwargs = {
        'inviter_email': inviter_entry['email'],
        'inviter_name': inviter_entry['username'],
        'support_email': ConfigSettings.EMAIL_SUPPORT,
        'admin_email': ConfigSettings.EMAIL_ADMIN,
        'url': ConfigSettings.INVITATION_URL_LOGIN,
        'user_email': invitation_entry.email,
        'domain': ConfigSettings.DOMAIN_NAME,
        'helpdesk_email': ConfigSettings.EMAIL_HELPDESK,
    }

    if project:
        subject = 'Welcome to the {} project!'.format(project['name'])
        if account_in_ad:
            template = 'invitation/ad_existing_invite_project.html'
        else:
            template = 'invitation/ad_invite_project.html'
        template_kwargs['project_name'] = project['name']
        template_kwargs['project_code'] = project['code']
        template_kwargs['project_role'] = invitation_entry.project_role
    else:
        subject = f'Welcome to {ConfigSettings.PROJECT_NAME}!'
        if not account_in_ad:
            template = 'invitation/ad_invite_without_project.html'
        else:
            template = 'invitation/ad_existing_invite_without_project.html'

        if invitation_entry.platform_role == 'admin':
            platform_role = 'Platform Administrator'
        else:
            platform_role = 'Platform User'
        template_kwargs['platform_role'] = platform_role

    attachment = []
    if not account_in_ad:
        if ConfigSettings.INVITE_ATTACHMENT:
            with open(ConfigSetting.INVITE_ATTACHMENT, 'rb') as f:
                data = base64.b64encode(f.read()).decode()
                attachment = [{'name': ConfigSetting.INVITE_ATTACHMENT_NAME, 'data': data}]

    email_sender.send(
        subject,
        invitation_entry.email,
        ConfigSettings.EMAIL_SUPPORT,
        msg_type='html',
        template=template,
        template_kwargs=template_kwargs,
        attachments=attachment,
    )
    if not account_in_ad:
        # send copy to admin
        email_sender.send(
            subject,
            ConfigSettings.EMAIL_ADMIN,
            ConfigSettings.EMAIL_SUPPORT,
            msg_type='html',
            template=template,
            template_kwargs=template_kwargs,
            attachments=attachment,
        )

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

import httpx

from app.config import ConfigSettings
from app.models.service_meta_class import MetaService


class SrvEmail(metaclass=MetaService):
    def send(
        self,
        subject: str,
        receiver: str,
        sender: str,
        content: str = '',
        msg_type: str = 'plain',
        template: str = None,
        template_kwargs: dict = None,
        attachments: list = [],
    ) -> None:

        '''
        Summary:
            The api is used to request a emailing sending operation
            by input payload

        Parameter:
            - subject(string): The subject of email
            - receiver(string): The reciever email
            - sender(string): The sender email
            - content(string): default="", The email content
            - msg_type(string): default="plain", the message type for email
            - template(string): default=None, email service support some predefined template
            - template_kwargs(dict): default={}, the parameters for the template structure

        Return:
            200 updated
        '''

        if not template_kwargs:
            template_kwargs = {}

        url = ConfigSettings.NOTIFY_SERVICE + 'email'
        payload = {
            'subject': subject,
            'sender': sender,
            'receiver': [receiver],
            'msg_type': msg_type,
            'attachments': attachments,
        }
        if content:
            payload['message'] = content
        if template:
            payload['template'] = template
            payload['template_kwargs'] = template_kwargs
        res = httpx.post(url=url, json=payload)
        return json.loads(res.text)

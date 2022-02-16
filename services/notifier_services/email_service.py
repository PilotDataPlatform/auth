import json

import requests

from config import ConfigSettings
from models.service_meta_class import MetaService


class SrvEmail(metaclass=MetaService):
    def send(self, subject, receiver, sender, content="", msg_type="plain", template=None, template_kwargs={}):
        url = ConfigSettings.EMAIL_SERVICE
        payload = {
            "subject": subject,
            "sender": sender,
            "receiver": [receiver],
            "msg_type": msg_type,
        }
        if content:
            payload["message"] = content
        if template:
            payload["template"] = template
            payload["template_kwargs"] = template_kwargs
        res = requests.post(
            url=url,
            json=payload
        )
        return json.loads(res.text)

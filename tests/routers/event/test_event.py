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

import mock
import pytest

from app.config import ConfigSettings
from app.resources.keycloak_api.ops_admin import OperationsAdmin
from uuid import uuid4


user_json = {
    'email': 'testuser@example.com',
    'enabled': True,
    'first_name': 'test',
    'id': uuid4(),
    'last_name': 'user',
    'name': 'testuser',
    'role': 'member',
    'username': 'testuser',
    'attributes': {'status': ['active']},
}

@mock.patch.object(OperationsAdmin, 'get_user_by_username', side_effect=None)
def test_create_event(get_user_mock, test_client, keycloak_admin_mock):
    get_user_mock.return_value = user_json
    payload = {
        'target_user': 'testuser',
        'operator': 'admin',
        'event_type': 'ACCOUNT_ACTIVATED',
        'detail': {},
    }
    response = test_client.post('/v1/events', json=payload)
    assert response.status_code == 200


@mock.patch.object(OperationsAdmin, 'get_user_by_username', side_effect=None)
def test_create_event_role(get_user_mock, test_client, keycloak_admin_mock):
    get_user_mock.return_value = user_json
    payload = {
        'target_user': 'testuser',
        'operator': 'admin',
        'event_type': 'ROLE_CHANGE',
        'detail': {
            'project_code': 'fakecode',
            'to': 'admin',
            'from': 'contributor',
        },
    }
    response = test_client.post('/v1/events', json=payload)
    assert response.status_code == 200


@mock.patch.object(OperationsAdmin, 'get_user_by_username', side_effect=None)
def test_create_event_invite(get_user_mock, test_client, keycloak_admin_mock):
    get_user_mock.return_value = user_json
    payload = {
        'operator': 'admin',
        'event_type': 'INVITE_TO_PROJECT',
        'detail': {
            'project_code': 'fakecode',
            'project_role': 'admin',
        },
    }
    response = test_client.post('/v1/events', json=payload)
    assert response.status_code == 200


@mock.patch.object(OperationsAdmin, 'get_user_by_username', side_effect=None)
def test_create_event_role_no_operator(get_user_mock, test_client, keycloak_admin_mock):
    get_user_mock.return_value = user_json
    payload = {
        'target_user': 'testuser',
        'operator': '',
        'event_type': 'ACCOUNT_ACTIVATED',
        'detail': {},
    }
    response = test_client.post('/v1/events', json=payload)
    assert response.status_code == 200


@pytest.mark.dependency(depends=["test_create_event", "test_create_event_role"])
def test_list_events_query_200(test_client):
    payload = {
        "project_code": "fakecode",
    }
    response = test_client.get('/v1/events', params=payload)
    assert response.status_code == 200
    for event in response.json()["result"]:
        if not event["event_type"] in ["ACCOUNT_ACTIVATED", "ACCOUNT_DISABLE"]:
            assert event["detail"]["project_code"] == "fakecode"



@pytest.mark.dependency(depends=["test_create_event", "test_create_event_role"])
def test_list_events_query_user_200(test_client):
    payload = {
        "user_id": user_json['id'],
    }
    response = test_client.get('/v1/events', params=payload)
    assert response.status_code == 200
    assert response.json()["result"][0]["target_user"] == user_json["username"]

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

import time
from uuid import uuid4

import pytest
from common import ProjectClient, ProjectNotFoundException

from app.config import ConfigSettings

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


PROJECT_DATA = {
    "id": str(uuid4()),
    "name": "Fake project",
    "code": "fakeproject",
}


class FakeProjectObject:
    id = PROJECT_DATA["id"]
    code = PROJECT_DATA["code"]
    name = PROJECT_DATA["name"]

    async def json(self):
        return PROJECT_DATA


def ops_admin_mock_client(monkeypatch, user_exists, relation=True, role="fakeproject-admin"):
    from app.resources.keycloak_api.ops_admin import OperationsAdmin

    class OperationsAdminMock:
        user_exists = ""
        role = ""
        relation = False

        def __init__(self, *args, **kwargs):
            pass

        def fake_init(self, *args, **kwargs):
            pass

        def get_user_by_email(self, anything):
            if self.user_exists:
                return user_json
            else:
                return None

        def get_user_by_username(self, anything):
            return user_json

        def get_user_realm_roles(self, anything):
            if self.relation:
                return [{"name": self.role}]
            else:
                return []

    ops_mock_client = OperationsAdminMock(user_exists=user_exists)
    ops_mock_client.user_exists = user_exists
    ops_mock_client.relation = relation
    ops_mock_client.role = role
    monkeypatch.setattr(OperationsAdmin, '__init__', ops_mock_client.fake_init)
    monkeypatch.setattr(OperationsAdmin, 'get_user_by_email', ops_mock_client.get_user_by_email)
    monkeypatch.setattr(OperationsAdmin, 'get_user_by_username', ops_mock_client.get_user_by_username)
    monkeypatch.setattr(OperationsAdmin, 'get_user_realm_roles', ops_mock_client.get_user_realm_roles)


@pytest.fixture
def ops_admin_mock(monkeypatch):
    return ops_admin_mock_client(monkeypatch, True)


@pytest.fixture
def ops_admin_mock_no_user(monkeypatch):
    return ops_admin_mock_client(monkeypatch, False)


@pytest.fixture
def ops_admin_mock_no_relation(monkeypatch):
    return ops_admin_mock_client(monkeypatch, True, relation=False)


@pytest.fixture
def ops_admin_mock_admin(monkeypatch):
    return ops_admin_mock_client(monkeypatch, True, role="platform-admin")


def ldap_mock_client(monkeypatch, user_exists, is_in_ad=True):
    from app.services.data_providers.ldap_client import LdapClient

    class LdapClientMock:
        user_data = ""
        user_exists = ""
        is_in_ad = True

        def __init__(self, *args, **kwargs):
            pass

        def fake_init(self):
            pass

        def connect(self):
            pass

        def is_account_in_ad(self, email):
            return self.is_in_ad

        def format_group_dn(self, group_name):
            return group_name

        def get_user_by_email(self, email):
            return 'user_dn', self.user_data

        def add_user_to_group(self, user_dn, group_dn):
            return ''

    ldap_mock_client = LdapClientMock()
    ldap_mock_client.user_data = {'username': 'testuser', 'email': 'testuser@example.com'}
    ldap_mock_client.user_exists = user_exists
    ldap_mock_client.is_in_ad = is_in_ad
    monkeypatch.setattr(LdapClient, 'connect', ldap_mock_client.connect)
    monkeypatch.setattr(LdapClient, 'is_account_in_ad', ldap_mock_client.is_account_in_ad)
    monkeypatch.setattr(LdapClient, 'format_group_dn', ldap_mock_client.format_group_dn)
    monkeypatch.setattr(LdapClient, 'get_user_by_email', ldap_mock_client.get_user_by_email)
    monkeypatch.setattr(LdapClient, 'add_user_to_group', ldap_mock_client.add_user_to_group)


@pytest.fixture
def ldap_mock(monkeypatch):
    return ldap_mock_client(monkeypatch, True)


@pytest.fixture
def ldap_mock_not_in_ad(monkeypatch):
    return ldap_mock_client(monkeypatch, True, is_in_ad=False)


@pytest.fixture
def ldap_mock_no_user(monkeypatch):
    return ldap_mock_client(monkeypatch, False)


@pytest.fixture
def patch_attachment(monkeypatch):
    monkeypatch.setattr(ConfigSettings, 'INVITE_ATTACHMENT', 'attachments/invite_attachment.pdf')


@pytest.mark.dependency()
def test_create_invitation_exists_in_ad(test_client, httpx_mock, ldap_mock, ops_admin_mock_no_user, mocker):
    mocker.patch.object(ProjectClient, 'get', return_value=FakeProjectObject())

    httpx_mock.add_response(
        method='POST', url=ConfigSettings.NOTIFY_SERVICE + 'email', json={'result': 'success'}, status_code=200
    )
    payload = {
        'email': 'test1@example.com',
        'platform_role': 'member',
        'relationship': {
            'project_code': 'fakeproject',
            'project_role': 'admin',
            'inviter': 'admin',
        },
        'invited_by': 'admin',
    }
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 200


@pytest.mark.dependency()
def test_create_invitation_no_ad(test_client, httpx_mock, ldap_mock, ops_admin_mock_no_user, mocker):
    mocker.patch.object(ProjectClient, 'get', return_value=FakeProjectObject())

    httpx_mock.add_response(
        method='POST', url=ConfigSettings.NOTIFY_SERVICE + 'email', json={'result': 'success'}, status_code=200
    )
    payload = {
        'email': 'test2@example.com',
        'platform_role': 'member',
        'relationship': {
            'project_code': 'fakeproject',
            'project_role': 'admin',
            'inviter': 'admin',
        },
        'invited_by': 'admin',
    }
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 200


def test_create_invitation_no_relation(test_client, httpx_mock, ldap_mock_no_user, ops_admin_mock_no_user, mocker):
    mocker.patch.object(ProjectClient, 'get', return_value=FakeProjectObject())
    httpx_mock.add_response(
        method='POST', url=ConfigSettings.NOTIFY_SERVICE + 'email', json={'result': 'success'}, status_code=200
    )
    payload = {'email': 'test3@example.com', 'platform_role': 'member', 'invited_by': 'admin'}
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 200


def test_create_invitation_admin(test_client, httpx_mock, ldap_mock_no_user, ops_admin_mock_no_user, mocker):
    mocker.patch.object(ProjectClient, 'get', return_value=FakeProjectObject())
    httpx_mock.add_response(
        method='POST', url=ConfigSettings.NOTIFY_SERVICE + 'email', json={'result': 'success'}, status_code=200
    )
    payload = {'email': 'test4@example.com', 'platform_role': 'admin', 'invited_by': 'admin'}
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 200


@pytest.mark.dependency(depends=['test_create_invitation_admin'])
def test_create_invitation_admin_already_exists(test_client, httpx_mock, ldap_mock, ops_admin_mock):
    payload = {'email': 'test4@example.com', 'platform_role': 'admin', 'invited_by': 'admin'}
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 400
    assert response.json()['result'] == '[ERROR] User already exists in platform'


@pytest.mark.dependency(depends=['test_create_invitation_no_ad'])
def test_create_invitation_already_exists_in_project(test_client, httpx_mock, ldap_mock, ops_admin_mock, mocker):
    mocker.patch.object(ProjectClient, 'get', return_value=FakeProjectObject())
    payload = {
        'email': 'test2@example.com',
        'platform_role': 'member',
        'relationship': {
            'project_code': 'fakeproject',
            'project_role': 'admin',
            'inviter': 'admin',
        },
        'invited_by': 'admin',
    }
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 409
    assert response.json()['result'] == 'Invitation for this user already exists'


def test_create_invitation_not_in_ad(
    test_client,
    httpx_mock,
    ldap_mock_not_in_ad,
    ops_admin_mock_no_user,
    patch_attachment,
    mocker,
):
    mocker.patch.object(ProjectClient, 'get', return_value=FakeProjectObject())

    httpx_mock.add_response(
        method='POST', url=ConfigSettings.NOTIFY_SERVICE + 'email', json={'result': 'success'}, status_code=200
    )
    payload = {
        'email': 'test3@example.com',
        'platform_role': 'member',
        'relationship': {
            'project_code': 'fakeproject',
            'project_role': 'admin',
            'inviter': 'admin',
        },
        'invited_by': 'admin',
    }
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 200


@pytest.mark.dependency(depends=['test_create_invitation_exists_in_ad'])
def test_get_invite_list(test_client, httpx_mock):
    payload = {
        'page': 0,
        'page_size': 1,
        'filters': {
            'project_code': 'fakeproject',
        },
    }
    response = test_client.post('/v1/invitation-list', json=payload)
    assert response.status_code == 200
    assert response.json()['result'][0]['project_code'] == 'fakeproject'


@pytest.mark.dependency(depends=['test_create_invitation_exists_in_ad'])
def test_get_invite_list_filter(test_client, httpx_mock):
    payload = {
        'page': 0,
        'page_size': 1,
        'filters': {
            'email': 'example.com',
        },
    }
    response = test_client.post('/v1/invitation-list', json=payload)
    assert response.status_code == 200
    assert response.json()['result'][0]['project_code'] == 'fakeproject'


@pytest.mark.dependency(depends=['test_create_invitation_exists_in_ad'])
def test_get_invite_list_order(test_client, httpx_mock, ldap_mock, ops_admin_mock_no_user):
    timestamp = time.time()
    httpx_mock.add_response(
        method='POST', url=ConfigSettings.NOTIFY_SERVICE + 'email', json={'result': 'success'}, status_code=200
    )
    payload = {'email': f'a@ordertest_{timestamp}.com', 'platform_role': 'admin', 'invited_by': 'admin'}
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 200
    payload = {'email': f'b@ordertest_{timestamp}.com', 'platform_role': 'admin', 'invited_by': 'admin'}
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 200
    payload = {'email': f'c@ordertest_{timestamp}.com', 'platform_role': 'admin', 'invited_by': 'admin'}
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 200

    payload = {
        'page': 0,
        'page_size': 5,
        'order_by': 'email',
        'order_type': 'desc',
        'filters': {
            'email': f'ordertest_{timestamp}.com',
        },
    }
    response = test_client.post('/v1/invitation-list', json=payload)
    assert response.status_code == 200
    assert len(response.json()['result']) == 3
    assert response.json()['result'][0]['email'] == f'c@ordertest_{timestamp}.com'
    assert response.json()['result'][1]['email'] == f'b@ordertest_{timestamp}.com'
    assert response.json()['result'][2]['email'] == f'a@ordertest_{timestamp}.com'


def test_check_invite_email(test_client, httpx_mock, ops_admin_mock, mocker):
    mocker.patch.object(ProjectClient, 'get', return_value=FakeProjectObject())
    payload = {
        'project_code': 'fakeproject',
    }
    response = test_client.get('/v1/invitation/check/testuser@example.com', params=payload)
    assert response.status_code == 200
    assert response.json()['result']['role'] == user_json['role']
    assert response.json()['result']['relationship']['project_code'] == 'fakeproject'


def test_check_invite_email_bad_project_id(test_client, httpx_mock, ops_admin_mock, mocker):
    mocker.patch.object(ProjectClient, 'get', side_effect=ProjectNotFoundException())

    payload = {
        'project_code': 'badcode',
    }
    response = test_client.get('/v1/invitation/check/testuser@example.com', params=payload)
    assert response.status_code == 404
    assert response.json()['error_msg'] == 'Project not found'


def test_check_invite_email_no_relation(test_client, httpx_mock, ops_admin_mock_no_relation, mocker):
    mocker.patch.object(ProjectClient, 'get', return_value=FakeProjectObject())
    payload = {
        'project_code': 'fakeproject',
    }
    response = test_client.get('/v1/invitation/check/testuser@example.com', params=payload)
    assert response.status_code == 200
    assert response.json()['result']['role'] == user_json['role']
    assert response.json()['result']['relationship'] == {}


def test_check_invite_email_platform_admin(test_client, httpx_mock, ops_admin_mock_admin, mocker):
    mocker.patch.object(ProjectClient, 'get', return_value=FakeProjectObject())
    payload = {
        'project_code': 'fakeproject',
    }
    response = test_client.get('/v1/invitation/check/testuser@example.com', params=payload)
    assert response.status_code == 200
    assert response.json()['result']['role'] == 'admin'
    assert response.json()['result']['relationship'] == {}


def test_check_invite_no_user(test_client, httpx_mock, ops_admin_mock_no_user):
    payload = {
        'project_code': 'fakeproject',
    }
    response = test_client.get('/v1/invitation/check/testuser@example.com', params=payload)
    assert response.status_code == 404
    assert response.json()['error_msg'] == 'User not found in keycloak'


@pytest.mark.dependency(name='create_for_update')
def test_invite_create_for_update(test_client, httpx_mock, ldap_mock, ops_admin_mock_no_user):
    httpx_mock.add_response(
        method='POST', url=ConfigSettings.NOTIFY_SERVICE + 'email', json={'result': 'success'}, status_code=200
    )
    payload = {'email': 'event@test.com', 'platform_role': 'admin', 'invited_by': 'admin'}
    response = test_client.post('/v1/invitations', json=payload)
    assert response.status_code == 200


@pytest.mark.dependency(depends=['create_for_update'])
def test_invite_update(test_client, httpx_mock, ops_admin_mock):
    payload = {
        'page': 0,
        'page_size': 5,
        'order_by': 'email',
        'order_type': 'desc',
        'filters': {
            'email': 'event@test.com',
        },
    }
    response = test_client.post('/v1/invitation-list', json=payload)
    assert response.status_code == 200
    invite_id = response.json()["result"][0]['id']

    payload = {
        'status': 'complete',
    }
    response = test_client.put(f'/v1/invitation/{invite_id}', json=payload)
    assert response.status_code == 200

    payload = {
        'invitation_id': invite_id,
    }
    response = test_client.get('/v1/events', params=payload)
    assert response.status_code == 200
    assert response.json()["result"][0]["target_user"] == user_json["username"]
    assert response.json()["result"][0]["target_user_id"] == str(user_json["id"])

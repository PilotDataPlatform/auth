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

from keycloak import exceptions
from uuid import uuid4

test_user = {
    'username': 'test_user',
    'email': 'test_user',
    'id': 'test_user',
    'firstName': 'firstName',
    'lastName': 'lastName',
    'attributes': {'status': ['active']},
}

# user authentication method


def test_authentication(test_client, mocker, keycloak_admin_mock):
    mocker.patch(
        'app.resources.keycloak_api.ops_user.OperationsUser.get_token',
        return_value={'access_token': 'test', 'refresh_token': 'test'},
    )
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_by_username', return_value=test_user)
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.update_user_attributes')

    response = test_client.post('/v1/users/auth', json={'username': 'test_user', 'password': 'test_user'})
    assert response.status_code == 200


def test_authentication_with_disable(test_client, mocker, keycloak_admin_mock):
    test_user_disable = {
        'username': 'test_user',
        'email': 'test_user',
        'id': 'test_user',
        'firstName': 'firstName',
        'lastName': 'lastName',
        'attributes': {'status': ['disabled']},
    }
    mocker.patch(
        'app.resources.keycloak_api.ops_user.OperationsUser.get_token',
        return_value={'access_token': 'test', 'refresh_token': 'test'},
    )
    mocker.patch(
        'app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_by_username', return_value=test_user_disable
    )

    response = test_client.post('/v1/users/auth', json={'username': 'test_user', 'password': 'test_user'})
    assert response.status_code == 401
    assert response.json().get('error_msg') == 'User is disabled'


def test_authentication_with_password_fail(test_client, mocker, keycloak_admin_mock):

    m = mocker.patch(
        'app.resources.keycloak_api.ops_user.OperationsUser.get_token',
        return_value={'access_token': 'test', 'refresh_token': 'test'},
    )
    m.side_effect = exceptions.KeycloakAuthenticationError

    response = test_client.post('/v1/users/auth', json={'username': 'test_user', 'password': 'test_user'})
    assert response.status_code == 401


def test_authentication_with_user_not_found(test_client, mocker, keycloak_admin_mock):

    m = mocker.patch(
        'app.resources.keycloak_api.ops_user.OperationsUser.get_token',
        return_value={'access_token': 'test', 'refresh_token': 'test'},
    )
    m.side_effect = exceptions.KeycloakGetError

    response = test_client.post('/v1/users/auth', json={'username': 'test_user', 'password': 'test_user'})
    assert response.status_code == 404


# refresh token tests
def test_token_refresh(test_client, mocker, keycloak_admin_mock):

    m = mocker.patch(
        'app.resources.keycloak_api.ops_user.OperationsUser.get_refresh_token',
        return_value={'access_token': 'test', 'refresh_token': 'test'},
    )

    response = test_client.post(
        '/v1/users/refresh',
        json={
            'refreshtoken': 'test_token',
        },
    )
    assert response.status_code == 200


def test_token_refresh_missing_payload(test_client, mocker, keycloak_admin_mock):

    m = mocker.patch(
        'app.resources.keycloak_api.ops_user.OperationsUser.get_refresh_token',
        return_value={'access_token': 'test', 'refresh_token': 'test'},
    )

    response = test_client.post('/v1/users/refresh', json={})
    assert response.status_code == 422


# user realm operation
def test_add_user_keycloak_realm_role(test_client, mocker, keycloak_admin_mock):

    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_by_email', return_value={'id': 'test'})
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.assign_user_role', return_value={})

    response = test_client.post('/v1/user/project-role', json={'email': 'test_email', 'project_role': 'test_project'})
    assert response.status_code == 200


def test_remove_user_keycloak_realm_role(test_client, mocker, keycloak_admin_mock):
    mocker.patch(
        'app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_by_email',
        return_value={'id': uuid4(), 'username': 'fakeuser'}
    )
    mocker.patch(
        'app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_by_username',
        return_value={'id': uuid4(), 'username': 'fakeuser'}
    )
    mocker.patch(
        'app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_realm_roles',
        return_value=[]
    )
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.delete_role_of_user', return_value={})
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.assign_user_role', return_value=None)

    response = test_client.delete(
        '/v1/user/project-role',
        json={
            'email': 'test_email',
            'project_role': 'test_project',
            'operator': 'admin',
            'project_code': 'fakecoderemove'
        }
    )
    assert response.status_code == 200


def create_test_user_list(size=10):
    user_list = []
    for x in range(size):
        user_list.append(
            {
                'username': 'test_user_%d' % x,
                'email': 'test_user_%d@email.com' % x,
                'id': 'test_user_%d' % x,
                'firstName': 'firstName_%d' % x,
                'lastName': 'lastName_%d' % x,
                'attributes': {'status': ['active']},
            }
        )

    return user_list


# list platform user test
def test_list_platform_user_pagination_1(test_client, mocker, keycloak_admin_mock):
    num_of_user = 20
    page_size = 10
    users = create_test_user_list(num_of_user)

    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_count', return_value=len(users))
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_all_users', return_value=users)
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_users_in_role', return_value=[])

    response = test_client.get('/v1/users', params={'page_size': page_size})
    assert response.status_code == 200
    assert len(response.json().get('result')) == page_size


def test_list_platform_user_pagination_2(test_client, mocker, keycloak_admin_mock):
    num_of_user = 20
    page_size = 5
    users = create_test_user_list(num_of_user)

    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_count', return_value=len(users))
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_all_users', return_value=users)
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_users_in_role', return_value=[])

    response = test_client.get('/v1/users', params={'page_size': page_size})
    assert response.status_code == 200
    assert len(response.json().get('result')) == page_size
    assert response.json().get('num_of_pages') == (num_of_user / page_size)


def test_list_platform_user_platform_admin_check(test_client, mocker, keycloak_admin_mock):
    num_of_user = 20
    users = create_test_user_list(num_of_user)

    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_count', return_value=len(users))
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_all_users', return_value=users)
    mocker.patch(
        'app.resources.keycloak_api.ops_admin.OperationsAdmin.get_users_in_role',
        return_value=[{'username': 'test_user_1'}],
    )

    response = test_client.get('/v1/users', params={})
    assert response.status_code == 200
    for x in response.json().get('result'):
        if x.get('username') == 'test_user_1':
            assert x.get('role') == 'admin'


def test_list_users_under_roles_filter_order_by_email(test_client, mocker, keycloak_admin_mock):
    num_of_user = 20
    page_size = 10
    users = create_test_user_list(num_of_user)

    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_count', return_value=len(users))
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_all_users', return_value=users)
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_users_in_role', return_value=[])

    response = test_client.get('/v1/users', params={'order_by': 'email', 'order_type': 'desc'})
    assert response.status_code == 200
    user_list = response.json().get('result')
    assert user_list[0].get('email') > user_list[1].get('email')


def test_list_users_under_roles_filter_order_by_username(test_client, mocker, keycloak_admin_mock):
    num_of_user = 20
    page_size = 10
    users = create_test_user_list(num_of_user)

    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_count', return_value=len(users))
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_all_users', return_value=users)
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_users_in_role', return_value=[])

    response = test_client.get('/v1/users', params={'order_by': 'username', 'order_type': 'desc'})
    assert response.status_code == 200
    user_list = response.json().get('result')
    assert user_list[0].get('email') > user_list[1].get('email')


def test_list_users_under_roles_filter_order_by_last_name(test_client, mocker, keycloak_admin_mock):
    num_of_user = 20
    page_size = 10
    users = create_test_user_list(num_of_user)

    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_count', return_value=len(users))
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_all_users', return_value=users)
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_users_in_role', return_value=[])

    response = test_client.get('/v1/users', params={'order_by': 'last_name', 'order_type': 'desc'})
    assert response.status_code == 200
    user_list = response.json().get('result')
    assert user_list[0].get('last_name') > user_list[1].get('last_name')


# disable/enable test

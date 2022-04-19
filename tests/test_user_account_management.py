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

from uuid import uuid4


def test_user_add_ad_group(test_client, mocker, ldap_client_mock):
    mocker.patch('app.services.data_providers.ldap_client.LdapClient.get_user_by_email', return_value=(None, None))
    mocker.patch('app.services.data_providers.ldap_client.LdapClient.format_group_dn')
    mocker.patch('app.services.data_providers.ldap_client.LdapClient.add_user_to_group')

    response = test_client.put(
        '/v1/user/ad-group',
        json={
            'user_email': 'test_email',
            'group_code': 'test_group',
            'operation_type': 'add',
        },
    )
    assert response.status_code == 200
    assert response.json().get('result') == '%s user %s from ad group' % ('add', 'test_email')


def test_user_remove_ad_group(test_client, mocker, ldap_client_mock):
    mocker.patch('app.services.data_providers.ldap_client.LdapClient.get_user_by_email', return_value=(None, None))
    mocker.patch('app.services.data_providers.ldap_client.LdapClient.format_group_dn')
    mocker.patch('app.services.data_providers.ldap_client.LdapClient.remove_user_from_group')

    response = test_client.put(
        '/v1/user/ad-group',
        json={
            'user_email': 'test_email',
            'group_code': 'test_group',
            'operation_type': 'remove',
        },
    )
    assert response.status_code == 200
    assert response.json().get('result') == '%s user %s from ad group' % ('remove', 'test_email')


# disable/enable user
def test_user_enable(test_client, mocker, keycloak_admin_mock):
    mocker.patch(
        'app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_by_email',
        return_value={'id': uuid4(), 'username': 'fakeuser'}
    )
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.update_user_attributes', return_value='')

    response = test_client.put(
        '/v1/user/account',
        json={
            'user_email': 'test_email',
            'operation_type': 'enable',
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('result') == '%s user %s' % ('enable', 'test_email')


def test_user_disable(test_client, mocker, keycloak_admin_mock, ldap_client_mock):
    mocker.patch(
        'app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_by_email',
        return_value={'id': uuid4(), 'username': 'fakeuser'}
    )
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.update_user_attributes', return_value='')

    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.get_user_realm_roles', return_value=[])
    mocker.patch('app.resources.keycloak_api.ops_admin.OperationsAdmin.remove_user_realm_roles', return_value='')

    mocker.patch(
        'app.services.data_providers.ldap_client.LdapClient.get_user_by_email', return_value=(None, {'memberOf': []})
    )

    response = test_client.put(
        '/v1/user/account',
        json={
            'user_email': 'test_email',
            'operation_type': 'disable',
        },
    )
    assert response.status_code == 200
    assert response.json().get('result') == '%s user %s' % ('disable', 'test_email')

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

def test_user_account_duplicate(test_client, mocker):
    mocker.patch('app.routers.accounts.AccountRequest.is_duplicate_user', return_value=True)

    response = test_client.post('/v1/accounts', json={'email': 'test_email', 'username': 'test_user'})
    assert response.status_code == 400


def test_user_account_user_dn_not_found(test_client, mocker, keycloak_admin_mock, ldap_client_mock):
    mocker.patch('app.routers.accounts.AccountRequest.is_duplicate_user', return_value=False)
    mocker.patch('app.services.data_providers.ldap_client.LdapClient.get_user_by_username', return_value=(None, None))
    mocker.patch('app.services.notifier_services.email_service.SrvEmail.send')
    mocker.patch('app.services.notifier_services.email_service.SrvEmail.send')

    response = test_client.post('/v1/accounts', json={'email': 'test_email', 'username': 'test_user'})
    assert response.status_code == 200
    assert response.json().get('result') == 'Request for a test account is under review'


def test_user_account_user_dn_exist(test_client, mocker, keycloak_admin_mock, ldap_client_mock):
    mocker.patch('app.routers.accounts.AccountRequest.is_duplicate_user', return_value=False)
    mocker.patch(
        'app.services.data_providers.ldap_client.LdapClient.get_user_by_username',
        return_value=(
            'user_dn',
            {
                'mail': [b'test_email'],
                'givenName': [b'test_user'],
                'sn': [b'test_user'],
            },
        ),
    )

    mocker.patch('app.services.data_providers.ldap_client.LdapClient.add_user_to_group')
    mocker.patch('app.services.data_providers.ldap_client.LdapClient.add_user_to_group')

    mocker.patch('app.services.notifier_services.email_service.SrvEmail.send')
    mocker.patch('app.services.notifier_services.email_service.SrvEmail.send')

    response = test_client.post('/v1/accounts', json={'email': 'test_email', 'username': 'test_user'})
    assert response.status_code == 200
    assert response.json().get('result') == 'Request for a test account has been approved'


def test_user_account_email_not_match(test_client, mocker, keycloak_admin_mock, ldap_client_mock):
    mocker.patch('app.routers.accounts.AccountRequest.is_duplicate_user', return_value=False)
    mocker.patch(
        'app.services.data_providers.ldap_client.LdapClient.get_user_by_username',
        return_value=(
            'user_dn',
            {
                'mail': [b'test_email_not_matched'],
                'givenName': [b'test_user'],
                'sn': [b'test_user'],
            },
        ),
    )

    mocker.patch('app.services.data_providers.ldap_client.LdapClient.add_user_to_group')
    mocker.patch('app.services.data_providers.ldap_client.LdapClient.add_user_to_group')

    mocker.patch('app.services.notifier_services.email_service.SrvEmail.send')
    mocker.patch('app.services.notifier_services.email_service.SrvEmail.send')

    response = test_client.post('/v1/accounts', json={'email': 'test_email', 'username': 'test_user'})
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('result') == 'Request for a test account is under review'

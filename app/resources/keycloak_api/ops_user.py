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

from keycloak import KeycloakOpenID

from app.config import ConfigSettings


class OperationsUser:
    def __init__(self, client_id, realm_name, client_secret_key):
        self.keycloak_openid = KeycloakOpenID(
            server_url=ConfigSettings.KEYCLOAK_SERVER_URL,
            client_id=client_id,
            realm_name=realm_name,
            client_secret_key=client_secret_key,
        )
        self.config_well_know = self.keycloak_openid.well_know()
        self.token = ''

    # Get Token
    def get_token(self, username, password):
        self.token = self.keycloak_openid.token(username, password)
        return self.token

    # Get Userinfo
    def get_userinfo(self):
        userinfo = self.keycloak_openid.userinfo(self.token['access_token'])
        return userinfo

    # Refresh token
    def get_refresh_token(self, token):
        self.token = self.keycloak_openid.refresh_token(token)
        return self.token

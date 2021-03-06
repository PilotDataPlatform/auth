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

from functools import lru_cache
from typing import Any, Dict, Optional

from common import VaultClient
from pydantic import BaseSettings, Extra


class VaultConfig(BaseSettings):
    """Store vault related configuration."""

    APP_NAME: str = 'service_auth'
    CONFIG_CENTER_ENABLED: bool = False

    VAULT_URL: Optional[str]
    VAULT_CRT: Optional[str]
    VAULT_TOKEN: Optional[str]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    config = VaultConfig()

    if not config.CONFIG_CENTER_ENABLED:
        return {}

    client = VaultClient(config.VAULT_URL, config.VAULT_CRT, config.VAULT_TOKEN)
    return client.get_from_vault(config.APP_NAME)


class Settings(BaseSettings):
    """Store service configuration settings."""

    APP_NAME: str = 'service_auth'
    VERSION: str = '0.1.0'
    PORT: int = 5061
    HOST: str = '0.0.0.0'
    env: str = ''
    namespace: str = ''

    NOTIFY_SERVICE: str
    PROJECT_SERVICE: str

    EMAIL_SUPPORT: str
    EMAIL_ADMIN: str
    EMAIL_HELPDESK: str

    # LDAP configs
    LDAP_URL: str
    LDAP_ADMIN_DN: str
    LDAP_ADMIN_SECRET: str
    LDAP_OU: str
    LDAP_DC1: str
    LDAP_DC2: str
    LDAP_objectclass: str
    LDAP_USER_GROUP: str
    LDAP_COMMON_NAME_PREFIX: str
    LDAP_USER_OBJECTCLASS: str

    # BFF RDS
    RDS_HOST: str
    RDS_PORT: str
    RDS_DBNAME: str
    RDS_USER: str
    RDS_PWD: str
    RDS_SCHEMA_PREFIX: str

    # Keycloak config
    KEYCLOAK_ID: str
    KEYCLOAK_SERVER_URL: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_SECRET: str
    KEYCLOAK_REALM: str

    DOMAIN_NAME: str
    START_PATH: str
    GUIDE_PATH: str

    TEST_PROJECT_CODE: str = 'test-project-code'
    TEST_PROJECT_ROLE: str = 'collaborator'
    TEST_PROJECT_NAME: str = 'Indoc Test Project'

    OPEN_TELEMETRY_ENABLED: bool = False
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831

    ENABLE_ACTIVE_DIRECTORY: bool = True
    AD_USER_GROUP: str
    AD_ADMIN_GROUP: str
    PROJECT_NAME: str

    INVITE_ATTACHMENT: str = ""
    INVITE_ATTACHMENT_NAME: str = ""
    INVITATION_URL_LOGIN: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return env_settings, load_vault_settings, init_settings, file_secret_settings

    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)
        self.NOTIFY_SERVICE += '/v1/'
        self.REDIS_URL = f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        self.RDS_DB_URI = f"postgresql://{self.RDS_USER}:{self.RDS_PWD}@{self.RDS_HOST}:{self.RDS_PORT}/{self.RDS_DBNAME}"


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings


ConfigSettings = get_settings()

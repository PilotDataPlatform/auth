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

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateSchema, CreateTable
from sqlalchemy_utils import create_database, database_exists
from testcontainers.postgres import PostgresContainer

from app import create_app
from app.config import ConfigSettings
from app.models.sql_invitation import InvitationModel
from app.models.sql_events import UserEventModel


@pytest.fixture
def keycloak_user_mock(monkeypatch):
    from app.resources.keycloak_api.ops_user import OperationsUser
    class OperationsUserMock:
        def __init__(self, *args, **kwargs):
            pass

        def fake_init(self, *args, **kwargs):
            pass
    ops_mock_client = OperationsUserMock()
    monkeypatch.setattr(OperationsUser, '__init__', ops_mock_client.fake_init)


@pytest.fixture
def keycloak_admin_mock(monkeypatch):
    from app.resources.keycloak_api.ops_admin import OperationsAdmin
    from app.resources.keycloak_api.ops_user import OperationsUser
    class OperationsAdminMock:
        def __init__(self, *args, **kwargs):
            pass

        def fake_init(self, *args, **kwargs):
            pass
    ops_mock_client = OperationsAdminMock()
    monkeypatch.setattr(OperationsAdmin, '__init__', ops_mock_client.fake_init)

    class OperationsUserMock:
        def __init__(self, *args, **kwargs):
            pass

        def fake_init(self, *args, **kwargs):
            pass
    ops_mock_client = OperationsUserMock()
    monkeypatch.setattr(OperationsUser, '__init__', ops_mock_client.fake_init)


@pytest.fixture
def ldap_client_mock(monkeypatch):
    from app.services.data_providers.ldap_client import LdapClient

    class LdapClientMock:
        def __init__(self, *args, **kwargs):
            pass

        def fake_init(self, *args, **kwargs):
            pass

        def connect(self, *args, **kwargs):
            pass

        def disconnect(self, *args, **kwargs):
            pass

        def format_group_dn(self, group_name):
            return group_name
    ldap_client = LdapClientMock()
    monkeypatch.setattr(LdapClient, '__init__', ldap_client.fake_init)
    monkeypatch.setattr(LdapClient, 'format_group_dn', ldap_client.format_group_dn)
    monkeypatch.setattr(LdapClient, 'connect', ldap_client.connect)
    monkeypatch.setattr(LdapClient, 'disconnect', ldap_client.disconnect)


@pytest.fixture(scope='session', autouse=True)
def db():
    with PostgresContainer('postgres:14.1') as postgres:
        postgres_uri = postgres.get_connection_url()
        if not database_exists(postgres_uri):
            create_database(postgres_uri)
        engine = create_engine(postgres_uri)

        from app.models.sql_invitation import Base
        CreateTable(InvitationModel.__table__).compile(dialect=postgresql.dialect())
        if not engine.dialect.has_schema(engine, ConfigSettings.RDS_SCHEMA_PREFIX + '_invitation'):
            engine.execute(CreateSchema(ConfigSettings.RDS_SCHEMA_PREFIX + '_invitation'))
        Base.metadata.create_all(bind=engine)

        from app.models.sql_events import Base
        CreateTable(UserEventModel.__table__).compile(dialect=postgresql.dialect())
        if not engine.dialect.has_schema(engine, ConfigSettings.RDS_SCHEMA_PREFIX + '_event'):
            engine.execute(CreateSchema(ConfigSettings.RDS_SCHEMA_PREFIX + '_event'))
        Base.metadata.create_all(bind=engine)
        yield postgres


@pytest.fixture
def test_client(db):
    ConfigSettings.RDS_DB_URI = db.get_connection_url()
    app = create_app()
    client = TestClient(app)
    return client

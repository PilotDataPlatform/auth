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

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from app.config import ConfigSettings

Base = declarative_base()


class InvitationModel(Base):
    __tablename__ = 'invitation'
    __table_args__ = {'schema': ConfigSettings.RDS_SCHEMA_PREFIX + '_invitation'}
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid4)
    invitation_code = Column(String())
    expiry_timestamp = Column(DateTime())
    create_timestamp = Column(DateTime(), default=datetime.utcnow)
    invited_by = Column(String())
    email = Column(String())
    platform_role = Column(String())
    project_role = Column(String())
    project_code = Column(String())
    status = Column(String())

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        result = {}
        field_list = [
            'id',
            'invitation_code',
            'expiry_timestamp',
            'create_timestamp',
            'invited_by',
            'email',
            'platform_role',
            'project_role',
            'project_code',
            'status',
        ]
        for field in field_list:
            if getattr(self, field):
                result[field] = str(getattr(self, field))
            else:
                result[field] = ""
        return result

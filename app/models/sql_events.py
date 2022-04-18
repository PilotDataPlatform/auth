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
from sqlalchemy import JSON

from app.config import ConfigSettings

Base = declarative_base()


class UserEventModel(Base):
    __tablename__ = 'user_event'
    __table_args__ = {'schema': ConfigSettings.RDS_SCHEMA_PREFIX + '_event'}
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid4)
    target_user_id = Column(UUID(as_uuid=True))
    target_user = Column(String())
    operator_id = Column(UUID(as_uuid=True), nullable=True)
    operator = Column(String())
    event_type = Column(String())
    timestamp = Column(DateTime(), default=datetime.utcnow)
    detail = Column(JSON())

    def to_dict(self):
        result = {}
        field_list = [
            'id',
            'target_user',
            'target_user_id',
            'operator',
            'operator_id',
            'event_type',
            'timestamp',
            'detail',
        ]
        for field in field_list:
            if field != "detail":
                if getattr(self, field):
                    result[field] = str(getattr(self, field))
                else:
                    result[field] = ""
            else:
                if not self.detail:
                    result["detail"] = {}
                else:
                    result[field] = getattr(self, field)
        return result

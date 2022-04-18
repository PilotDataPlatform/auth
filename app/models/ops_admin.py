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

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.types import constr


class UserGroupPOST(BaseModel):

    username: str
    groupname: str


class UserOpsPOST(BaseModel):
    class Announcement(BaseModel):
        project_code: str
        announcement_pk: str

    username: str
    last_login: Optional[bool]
    announcement: Optional[Announcement]


class RealmRolesPOST(BaseModel):

    project_roles: list
    project_code: str


class UserInRolePOST(BaseModel):
    role_names: list
    username: str = None
    email: str = None
    page: int = 0
    page_size: int = 10
    order_by: str = None
    order_type: str = 'asc'
    status: str = 'active'

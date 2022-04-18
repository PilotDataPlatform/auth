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


class UserAuthPOST(BaseModel):
    """user authentication model."""
    username: str
    password: str
    # realm: str


class UserTokenRefreshPOST(BaseModel):
    """user token refresh model."""
    # realm: str
    refreshtoken: str


class UserLastLoginPOST(BaseModel):
    username: str


class UserProjectRolePOST(BaseModel):
    email: str
    project_role: str
    operator: str = ""
    project_code: str = ""
    invite_event: bool = False


class UserProjectRolePUT(BaseModel):
    email: str
    project_role: str
    operator: str
    project_code: str


class UserProjectRoleDELETE(BaseModel):
    email: str
    project_role: str
    operator: str
    project_code: str


class UserAnnouncementPOST(BaseModel):
    project_code: str
    announcement_pk: str
    username: str

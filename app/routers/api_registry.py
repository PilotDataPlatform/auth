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

from fastapi import FastAPI

from app.routers import accounts, ops_admin, ops_user, user_account_management
from app.routers.invitation import invitation
from app.routers.permissions import permissions
from app.routers.event import event


def api_registry(app: FastAPI):
    # app.include_router(api_root.router)
    app.include_router(ops_user.router, prefix='/v1')
    app.include_router(user_account_management.router, prefix='/v1')
    app.include_router(permissions.router, prefix='/v1')
    app.include_router(accounts.router, prefix='/v1')
    app.include_router(ops_admin.router, prefix='/v1')
    app.include_router(invitation.router, prefix='/v1')
    app.include_router(event.router, prefix='/v1')

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

import httpx

from app.config import ConfigSettings
from app.models.api_response import EAPIResponseCode
from app.resources.error_handler import APIException


def get_project_by_geid(geid: str) -> dict:
    payload = {'global_entity_id': geid}
    response = httpx.post(ConfigSettings.NEO4J_SERVICE + 'nodes/Container/query', json=payload)
    if not response.json():
        raise APIException(status_code=EAPIResponseCode.not_found.value, error_msg=f'Project not found: {geid}')
    return response.json()[0]

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

import requests
from pytz import timezone

from app.config import ConfigSettings


def mask_email(email):
    sections = email.split('@')
    first = ''.join(['*' for i in sections[0][0:-2]])
    second = ''.join([i if i == '.' else '*' for i in sections[1]])
    return sections[0][0] + first + sections[0][-1] + '@' + second


def get_formatted_datetime(tz):
    cet = timezone(tz)
    now = datetime.now(cet)
    return now.strftime('%Y-%m-%d, %-I:%M%p (%Z)')

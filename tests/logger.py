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

import logging
import os
from logging.handlers import RotatingFileHandler


class Logger(object):
    def __init__(self, name='log'):
        if not os.path.exists('./tests/logs/'):
            os.makedirs('./tests/logs/')
        if os.path.isfile('./tests/logs/' + name):
            os.remove('./tests/logs/' + name)
        self.name = name
        self.logger = logging.getLogger(name)
        level = logging.INFO

        self.logger.setLevel(level)
        fh = RotatingFileHandler('./tests/logs/' + name, maxBytes=500000, backupCount=1)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

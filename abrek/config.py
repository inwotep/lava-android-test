# Copyright (c) 2010 Linaro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

class AbrekConfig(object):
    def __init__(self):
        home = os.environ.get('HOME', '/')
        baseconfig = os.environ.get('XDG_CONFIG_HOME',
                     os.path.join(home, '.config'))
        basedata = os.environ.get('XDG_DATA_HOME',
                     os.path.join(home, '.local', 'share'))
        self.configdir = os.path.join(baseconfig, 'abrek')
        self.installdir = os.path.join(basedata, 'abrek', 'installed-tests')
        self.resultsdir = os.path.join(basedata, 'abrek', 'results')

_config = None

def get_config():
    global _config
    if _config is not None:
        return _config
    return AbrekConfig()

def set_config(config):
    global _config
    _config = config


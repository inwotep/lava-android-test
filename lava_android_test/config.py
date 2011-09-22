# Copyright (c) 2010-2011 Linaro

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
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


class LavaAndroidTestConfig(object):
    def __init__(self):
        home = os.environ.get('ANDROID_TEST_HOME', '/data/lava-android-test/')
        config = os.environ.get('ANDROID_TEST_CONFIG_HOME',
                     os.path.join(home, '.config'))
        basedata = os.environ.get('ANDROID_TEST_DATA_HOME',
                     os.path.join(home, 'share'))
        self.configdir = config
        self.installdir_android = os.path.join(basedata, 'installed-tests')
        self.resultsdir_android = os.path.join(basedata, 'results')
        self.tempdir_android = os.path.join(home, 'temp')
        self.tempdir_host = os.environ.get('ANDROID_TEST_TEMP_HOST', '/tmp/lava-android-test')

_config = None

def get_config():
    global _config
    if _config is not None:
        return _config
    return LavaAndroidTestConfig()

def set_config(config):
    global _config
    _config = config


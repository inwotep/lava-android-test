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
import sys
import subprocess
import shutil
from tempfile import mkdtemp
from lava_android_test.config import get_config, set_config
from lava_tool.dispatcher import LavaDispatcher, run_with_dispatcher_class

class LAVAAndroidTestDispatcher(LavaDispatcher):
    toolname = 'lava_android_test'
    description = """
    LAVA Android Test wrapper framework
    """
    epilog = """
    Please report all bugs using the Launchpad bug tracker:
    http://bugs.launchpad.net/lava-android-test/+filebug
    """
def check_adb_installed():
        rc = subprocess.call(["which", "adb"], stdout=open('/dev/null', 'w'))
        return rc == 0

def main():
    if not check_adb_installed():
        print >> sys.stderr, "Can't find the command adb."
        print >> sys.stderr, "Please add the path of adb command to PATH environment."
        sys.exit(1)

    try:
        config = get_config()
        if not os.path.exists(config.tempdir_host):
            os.makedirs(config.tempdir_host)
        config.tempdir_host = mkdtemp(dir=config.tempdir_host)
        set_config(config)
        os.chmod(config.tempdir_host, 0755)
        run_with_dispatcher_class(LAVAAndroidTestDispatcher)
    finally:
        shutil.rmtree(config.tempdir_host)

if __name__ == '__main__':
    main()

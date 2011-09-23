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

import sys
import pexpect
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
def check_adb_installed(self):
        rc = pexpect.run('adb', timeout=None, logfile=sys.stdout, withexitstatus=True)[1]
        return rc == 0


def main():
    if not check_adb_installed():
        print >> sys.stderr, "Can't find the command adb."
        print >> sys.stderr, "Please add the to PATH environment."
        sys.exit(1)

    run_with_dispatcher_class(LAVAAndroidTestDispatcher)

if __name__ == '__main__':
    main()

# Copyright (c) 2010, 2011 Linaro
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
import versiontools
from lava_tool.interface import Command
from lava_android_test.adb import ADB


class list_devices(Command):
    """
    List available devices
    .. program:: lava-android-test list-devices
    """

    def invoke(self):
        self.adb = ADB()
        
        try:
            (ret_code, output) = self.adb.devices()
            if output is not None:
                for line in output:
                    print line.strip()
            else:
                print "No device attached"
        except OSError:
            print "No device attached"
            
class list_tests(Command):
    """
    List available tests
    .. program:: lava-android-test list-tests
    """

    def invoke(self):
        from lava_android_test import test_definitions
        from pkgutil import walk_packages
        print "Known tests:"
        for importer, mod, ispkg in walk_packages(test_definitions.__path__):
            print mod

class list_installed(Command):
    """
    List installed tests for specified device.
    .. program:: lava-android-test list-tests
    .. program:: lava-android-test list-tests -s device_serial
    """
    def invoke(self):
        pass
            
class install(Command):
    """
    Install test to the specified device.
    .. program:: lava-android-test install test-id 
    .. program:: lava-android-test install test-id -s device_serial
    """
    def invoke(self):
        pass

class uninstall(Command):
    """
    Unistall test of the specified device.
    .. program:: lava-android-test uninstall test-id 
    .. program:: lava-android-test uninstall test-id -s device_serial
    """
    def invoke(self):
        pass

class run(Command):
    """
    Run a previously installed test program on the specified device
    .. program:: lava-android-test run test-id 
    .. program:: lava-android-test run test-id -s device_serial
    """
    def invoke(self):
        pass
    
class parse(Command):
    """
    Parse the results of previous test that run on the specified device
    .. program:: lava-android-test parse test-result-id 
    .. program:: lava-android-test parse test-result-id -s device_serial
    """
    def invoke(self):
        pass

class show(Command):
    """
    Display the output from a previous test that run on the specified device
    .. program:: lava-android-test show test-id 
    .. program:: lava-android-test show test-id -s device_serial
    """
    def invoke(self):
        pass


class version(Command):
    """
    Show LAVA Test version
    """

    def invoke(self):
        self.say("version details:")
        for framework in self._get_frameworks():
            self.say(" - {framework}: {version}",
                     framework=framework.__name__,
                     version=versiontools.format_version(
                         framework.__version__, framework))

    def _get_frameworks(self):
        import lava_tool
        import lava_android_test
        import linaro_dashboard_bundle
        import linaro_json
        return [
            lava_android_test,
            lava_tool,
            linaro_dashboard_bundle,
            linaro_json]
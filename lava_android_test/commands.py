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
from lava_tool.interface import Command as LAVACommand
from lava_tool.interface import LavaCommandError

from lava_android_test.adb import ADB
from lava_android_test.config import get_config
from lava_android_test.testdef import testloader

class Command(LAVACommand):

    def __init__(self, parser, args):
        super(Command, self).__init__(parser, args)
#        self._config = get_config()
#        self._test_loader = TestLoader(self._config)

    @classmethod
    def register_arguments(cls, parser):
        parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            default=False,
            help="Be less verbose about undertaken actions")
        parser.add_argument(
            "-Q", "--quiet-subcommands",
            action="store_true",
            default=False,
            help="Hide the output of all sub-commands (including tests)")

    def say(self, text, *args, **kwargs):
        print "LAVA:", text.format(*args, **kwargs)

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
        self.say("Known tests:") 
        for importer, mod, ispkg in walk_packages(test_definitions.__path__):
            self.say(" - {test_id}", test_id=mod)

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
        

class AndroidCommand(Command):
    
    @classmethod
    def register_arguments(self, parser):
        super(AndroidCommand, self).register_arguments(parser)
        group = parser.add_argument_group("specify device serial number")
        group.add_argument("-s", "--serial",
                            default=None,
                            metavar="FILE",
                            help=("specify the device with serial number"
                                 "that this command will be run on"))

class AndroidTestCommand(AndroidCommand):
    @classmethod
    def register_arguments(self, parser):
        super(AndroidTestCommand, self).register_arguments(parser)
        parser.add_argument("test_id",
                            help="Test identifier")

class AndroidResultCommand(AndroidCommand):
    @classmethod
    def register_arguments(self, parser):
        super(AndroidResultCommand, self).register_arguments(parser)
        parser.add_argument("result_id",
                            help="Test result identifier")

class list_installed(AndroidCommand):
    """
    List installed tests for specified device.
    .. program:: lava-android-test list-tests
    .. program:: lava-android-test list-tests -s device_serial
    """ 
    def invoke(self):
        config = get_config()
        self.adb = ADB(self.args.serial)
        
        self.say("Installed tests:")
        try:
            (ret_code, output) = self.adb.listdir(config.installdir_android)
            if output is not None:
                for dir in output:
                    self.say(" - {test_id}", test_id=dir.strip())
            else:
                self.say("No tests installed")
        except OSError:
            self.say("No tests installed")
            
class install(AndroidTestCommand):
    """
    Install test to the specified device.
    .. program:: lava-android-test install test-id 
    .. program:: lava-android-test install test-id -s device_serial
    """
    def invoke(self):
        test = testloader(self.args.test_id, self.args.serial)
        try:
            test.install()
        except Exception as strerror:
            raise LavaCommandError("Test installation error: %s" % strerror)

class uninstall(AndroidTestCommand):
    """
    Unistall test of the specified device.
    .. program:: lava-android-test uninstall test-id 
    .. program:: lava-android-test uninstall test-id -s device_serial
    """
    def invoke(self):
        test = testloader(self.args.test_id, self.args.serial)
        try:
            test.uninstall()
        except Exception as strerror:
            raise LavaCommandError("Test uninstall error: %s" % strerror)

class run(AndroidTestCommand):
    """
    Run a previously installed test program on the specified device
    .. program:: lava-android-test run test-id 
    .. program:: lava-android-test run test-id -s device_serial
    """
    def invoke(self):
        self.adb = ADB(self.args.serial)
        test = testloader(self.args.test_id, self.args.serial)
        try:
            result_id = test.run(quiet=self.args.quiet)
#            if self.args.output:
#                from lava_android_test.dashboard import generate_bundle
#                import json
#                bundle = generate_bundle(result_id, ADB(self.opts.serial))
#                with open(self.opts.output, "wt") as stream:
#                    json.dump(bundle, stream)
        except Exception as strerror:
            raise LavaCommandError("Test execution error: %s" % strerror)
    
class parse(AndroidResultCommand):
    """
    Parse the results of previous test that run on the specified device
    .. program:: lava-android-test parse test-result-id 
    .. program:: lava-android-test parse test-result-id -s device_serial
    """
    def invoke(self):
        pass

class show(AndroidResultCommand):
    """
    Display the output from a previous test that run on the specified device
    .. program:: lava-android-test show test-id 
    .. program:: lava-android-test show test-id -s device_serial
    """
    def invoke(self):
        pass


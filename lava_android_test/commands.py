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
import os
import base64
import versiontools
import inspect

from lava_tool.interface import Command as LAVACommand
from lava_tool.interface import LavaCommandError
from linaro_dashboard_bundle.io import DocumentIO

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
        
    def display_subprocess_output(self, stream_name, line):
        if self.args.quiet_subcommands:
            return
        if stream_name == 'stdout':
            self.say('(stdout) {0}', line.rstrip())
        elif stream_name == 'stderr':
            self.say('(stderr) {0}', line.rstrip())
            
class list_devices(Command):
    """
    List available devices
    program::lava-android-test list-devices
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
    program:: lava-android-test list-tests
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
                            metavar="serial",
                            help=("specify the device with serial number"
                                 "that this command will be run on"))
    def test_installed(self,test_id):
        if self.adb is None:
            self.adb = ADB()
        config = get_config()
        test_dir = os.path.join(config.installdir_android, test_id)
        return self.adb.exists(test_dir)

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
    program:: lava-android-test list-tests
    program:: lava-android-test list-tests -s device_serial
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

class list_results(AndroidCommand):
    """
    List results of tests that has been run on the  specified device.
    program:: lava-android-test list-results
    program:: lava-android-test list-results -s device_serial
    """ 
    def invoke(self):
        config = get_config()
        self.adb = ADB(self.args.serial)
        self.say("Saved results:")
        try:
            (ret_code, output)=self.adb.listdir(config.resultsdir_android)
            if ret_code != 0:
                raise OSError()
            for dir in output:
                self.say(" - {result_id}", result_id=dir.strip())
        except OSError:
            self.say("No results found")
            
class install(AndroidTestCommand):
    """
    Install test to the specified device.
    program:: lava-android-test install test-id 
    program:: lava-android-test install test-id -s device_serial
    """
    def invoke(self):
        self.adb = ADB(self.args.serial)
        if self.test_installed(self.args.test_id):
            raise LavaCommandError("The test (%s) has already installed." % self.args.test_id)
        test = testloader(self.args.test_id, self.args.serial)
        try:
            test.install()
        except Exception as strerror:
            raise LavaCommandError("Test installation error: %s" % strerror)

class uninstall(AndroidTestCommand):
    """
    Unistall test of the specified device.
    program:: lava-android-test uninstall test-id 
    program:: lava-android-test uninstall test-id -s device_serial
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
    program:: lava-android-test run test-id 
    program:: lava-android-test run test-id -s device_serial
    """
    def invoke(self):
        self.adb = ADB(self.args.serial)
        if not self.test_installed(self.args.test_id):
            raise LavaCommandError("The test (%s) has not been installed yet." % self.args.test_id)
        
        test = testloader(self.args.test_id, self.args.serial)
        try:
            test.run(quiet=self.args.quiet)
        except Exception as strerror:
            raise LavaCommandError("Test execution error: %s" % strerror)
    
class parse(AndroidResultCommand):
    """
    Parse the results of previous test that run on the specified device
    program:: lava-android-test parse test-result-id 
    program:: lava-android-test parse test-result-id -s device_serial
    """
    def invoke(self):
        self.adb = ADB(self.args.serial)
        config = get_config()
        resultdir = os.path.join(config.resultsdir_android, self.args.result_id)
        if not self.adb.exists(resultdir):
            raise  LavaCommandError("The result (%s) is not existed." % self.args.result_id)
        
        bundle_text = self.adb.read_file(os.path.join(resultdir, "testdata.json")).read()
        fmt, bundle = DocumentIO.loads(bundle_text)
        test = testloader(bundle['test_runs'][0]['test_id'])
        
        test.parse(self.args.result_id)
        output_text = self.adb.read_file(os.path.join(resultdir, os.path.basename(test.org_ouput_file))).read()
        bundle['test_runs'][0]["test_results"] = test.parser.results["test_results"]
        bundle['test_runs'][0]["attachments"] = [
            {
                "pathname": test.org_ouput_file,
                "mime_type": "text/plain",
                "content":  base64.standard_b64encode(output_text)
            }
        ]
        try:
            print DocumentIO.dumps(bundle)
        except IOError:
            pass

class show(AndroidResultCommand):
    """
    Display the output from a previous test that run on the specified device
    program:: lava-android-test show result-id 
    program:: lava-android-test show result-id -s device_serial
    """
    def invoke(self):
        self.adb = ADB(self.args.serial)
        config = get_config()
        resultsdir = os.path.join(config.resultsdir_android, self.args.result_id)
        if not self.adb.exists(resultsdir):
            raise  LavaCommandError("The result (%s) is not existed." % self.args.result_id)
        
        stdout = os.path.join(resultsdir, "stdout.log")
        if not self.adb.exists(stdout):
            self.say("No result found for '%s'" % self.args.result_id)
            return
        try:
            output = self.adb.read_file(stdout)
            if output is not None:
                for line in output.readlines():
                    self.display_subprocess_output('stdout', line)
        except IOError:
            pass
        
        stderr = os.path.join(resultsdir, "stderr.log")
        if not self.adb.exists(stderr):
            return
        try:
            output = self.adb.read_file(stderr)
            if output is not None:
                for line in output.readlines():
                    self.display_subprocess_output('stderr', line)
        except IOError:
            pass

class rename(AndroidResultCommand):
    """
    Rename the result's id of a previous test that run on the specified device
    program:: lava-android-test rename result-id result-id-new 
    program:: lava-android-test remove result-id result-id-new -s device_serial
    """
    
    @classmethod
    def register_arguments(self, parser):
        super(rename, self).register_arguments(parser)
        parser.add_argument("result_id_new",
                            help="New test result identifier")
    def invoke(self):
        config = get_config()
        srcdir = os.path.join(config.resultsdir_android, self.args.result_id)
        destdir = os.path.join(config.resultsdir_android, self.args.result_id_new)
        adb = ADB(self.args.serial)
        if not adb.exists(srcdir):
            self.say("Result (%s) not found" % self.args.result_id)
            return 
        if adb.exists(destdir):
            self.say("Destination result name already exists")
        adb.move(srcdir, destdir)

class remove(AndroidResultCommand):
    """
    Remove the result of a previous test that run on the specified device
    program:: lava-android-test remove result-id
    program:: lava-android-test remove result-id -s device_serial
    """
    
    @classmethod
    def register_arguments(self, parser):
        super(remove, self).register_arguments(parser)
        group = parser.add_argument_group("force to remove")
        group.add_argument("-f", "--force",
                            default=None,
                            help=("give an interactive question about remove"))
    
    def invoke(self):
        config = get_config()
        resultsdir = os.path.join(config.resultsdir_android, self.args.result_id)
        adb = ADB(self.args.serial)
        if not adb.exists(resultsdir):
            self.say("No result found for '%s'" % self.args.result_id)
            return
        if not self.args.force:
            self.say("Remove result '%s' for good? [Y/N]" % self.args.result_id)
            response = raw_input()
            if response[0].upper() != 'Y':
                return
        adb.rmtree(resultsdir)

# Copyright (c) 2011, 2012 Linaro
#
# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.

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
import urlparse
import versiontools

from lava_tool.interface import Command as LAVACommand
from lava_tool.interface import LavaCommandError
from linaro_dashboard_bundle.io import DocumentIO

from lava_android_test.adb import ADB
from lava_android_test.config import get_config
from lava_android_test.testdef import testloader, AndroidTest
from lava_android_test.testdef import AndroidTestRunner, \
                                      AndroidTestInstaller, \
                                      AndroidTestParser


class Command(LAVACommand):

    def __init__(self, parser, args):
        super(Command, self).__init__(parser, args)
        self.config = get_config()
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

    def say_begin(self, text, *args, **kwargs):
        print "LAVA: --Start Operation: ", text.format(*args, **kwargs)

    def say_end(self, text, *args, **kwargs):
        print "LAVA: --End Operation: ", text.format(*args, **kwargs),

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
            output = self.adb.devices()[1]
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
        return [
            lava_android_test,
            lava_tool,
            linaro_dashboard_bundle]


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

    def test_installed(self, test_id):
        if self.adb is None:
            self.adb = ADB()
        test_dir = os.path.join(self.config.installdir_android, test_id)
        return self.adb.exists(test_dir)

    def assertDeviceIsConnected(self):
        if not self.adb.isDeviceConnected():
            if self.adb.serial:
                raise Exception("Device '%s' is not connected" %
                                       self.adb.serial)
            else:
                raise Exception("No device found")

    def invoke(self):
        self.adb = ADB(self.args.serial)
        try:
            self.assertDeviceIsConnected()
        except Exception as err:
            raise LavaCommandError(err)

        self.invoke_sub()

    def invoke_sub():
        raise NotImplementedError


class AndroidTestCommand(AndroidCommand):
    @classmethod
    def register_arguments(self, parser):
        super(AndroidTestCommand, self).register_arguments(parser)
        parser.add_argument("test_id",
                            help="Test identifier")

    def get_tip_msg(self, text):
        if self.args.serial:
            tip_msg = "%s (%s) on device(%s)" % (text,
                                                 self.args.test_id,
                                                 self.args.serial)
        else:
            tip_msg = "%s (%s)" % (text, self.args.test_id)
        return tip_msg


class AndroidResultCommand(AndroidCommand):
    @classmethod
    def register_arguments(self, parser):
        super(AndroidResultCommand, self).register_arguments(parser)
        parser.add_argument("result_id",
                            help="Test result identifier")


class AndroidResultsCommand(AndroidCommand):
    @classmethod
    def register_arguments(self, parser):
        super(AndroidResultsCommand, self).register_arguments(parser)
        parser.add_argument("result_id", nargs="+",
                            help="One or more result identifiers")


class list_installed(AndroidCommand):
    """
    List installed tests for specified device.
    program:: lava-android-test list-tests
    program:: lava-android-test list-tests -s device_serial
    """
    def invoke_sub(self):

        self.say("Installed tests:")
        try:
            output = self.adb.listdir(self.config.installdir_android)[1]
            if output is not None:
                for dir_name in output:
                    self.say(" - {test_id}", test_id=dir_name.strip())
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
    def invoke_sub(self):
        self.say("Saved results:")
        try:
            (ret_code, output) = self.adb.listdir(
                                        self.config.resultsdir_android)
            if ret_code != 0:
                raise OSError()
            for dir_name in output:
                self.say(" - {result_id}", result_id=dir_name.strip())
        except OSError:
            self.say("No results found")


class install(AndroidTestCommand):
    """
    Install test to the specified device.
    program:: lava-android-test install test-id
    program:: lava-android-test install test-id -s device_serial
    """

    @classmethod
    def register_arguments(cls, parser):
        super(cls, install).register_arguments(parser)
        parser.add_argument('-o', '--install-option')

    def invoke_sub(self):
        tip_msg = self.get_tip_msg("Install test")
        self.say_begin(tip_msg)

        if self.test_installed(self.args.test_id):
            raise LavaCommandError("The test (%s) has already installed." %
                                   self.args.test_id)
        test = testloader(self.args.test_id, self.args.serial)
        try:
            test.install(self.args.install_option)
        except Exception as strerror:
            raise LavaCommandError("Test installation error: %s" % strerror)

        self.say_end(tip_msg)


class uninstall(AndroidTestCommand):
    """
    Unistall test of the specified device.
    program:: lava-android-test uninstall test-id
    program:: lava-android-test uninstall test-id -s device_serial
    """
    def invoke_sub(self):
        tip_msg = self.get_tip_msg("Uninstall test")
        self.say_begin(tip_msg)

        test = testloader(self.args.test_id, self.args.serial)
        try:
            test.uninstall()
        except Exception as strerror:
            raise LavaCommandError("Test uninstall error: %s" % strerror)
        self.say_end(tip_msg)


class run(AndroidTestCommand):
    """
    Run a previously installed test program on the specified device
    program:: lava-android-test run test-id
    program:: lava-android-test run test-id -s device_serial
    program:: lava-android-test run test-id -s device_serial -o outputfile
    """

    @classmethod
    def register_arguments(cls, parser):
        super(run, cls).register_arguments(parser)
        parser.add_argument('-O', '--run-option',
                    help=("Specified in the job file for using in "
                          "the real test action, so that we can customize"
                          " some test when need"))
        group = parser.add_argument_group("specify the bundle output file")
        group.add_argument("-o", "--output",
                            default=None,
                            metavar="FILE",
                           help=("After running the test parse the result"
                                 " artefacts, fuse them with the initial"
                                 " bundle and finally save the complete bundle"
                                 " to the  specified FILE."))

    def invoke_sub(self):
        tip_msg = self.get_tip_msg("Run test")
        self.say_begin(tip_msg)

        if not self.test_installed(self.args.test_id):
            raise LavaCommandError(
                "The test (%s) has not been installed yet." %
                self.args.test_id)
        test = testloader(self.args.test_id, self.args.serial)

        if not self.test_installed(test.testname):
            raise LavaCommandError(
                    "The test (%s) has not been installed yet."
                    % self.args.test_id)

        try:
            result_id = test.run(quiet=self.args.quiet,
                                  run_options=self.args.run_option)
            if self.args.output:
                output_dir = os.path.dirname(self.args.output)
                if output_dir and (not os.path.exists(output_dir)):
                    os.makedirs(output_dir)
                bundle = generate_bundle(self.args.serial, result_id)
                with open(self.args.output, "wt") as stream:
                    DocumentIO.dump(stream, bundle)

        except Exception as strerror:
            raise LavaCommandError("Test execution error: %s" % strerror)

        self.say_end(tip_msg)


class run_custom(AndroidCommand):
    """
    Run the command(s) that specified by the -c option in the command line
    program:: lava-android-test run-custom -c 'command1' -c 'command2' -p 'parse-regex1'
    program:: lava-android-test run test-id -s device_serial
    program:: lava-android-test run test-id -s device_serial -o outputfile
    """

    @classmethod
    def register_arguments(cls, parser):
        super(run_custom, cls).register_arguments(parser)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-c', '--android-command', action='append',
                            help=("Specified in the job file for using"
                                  " in the real test action, so that "
                                  "we can customize some test when need"))
        group.add_argument('-f', '--command-file',
                            help=("Specified the command file that will be "
                                  "pushed into android and run."))
        parser.add_argument('-p', '--parse-regex',
                            help=("Specified the regular expression used"
                                  " for analyzing command output"))
        group = parser.add_argument_group("specify the bundle output file")
        group.add_argument("-o", "--output",
                            default=None,
                            metavar="FILE",
                           help=("After running the test parse the result"
                                 " artefacts, fuse them with the initial"
                                 " bundle and finally save the complete bundle"
                                 " to the  specified FILE."))

    def invoke_sub(self):

        config = get_config()
        test_name = 'custom'
        ADB_SHELL_STEPS = []
        STEPS_HOST_PRE = []
        STEPS_ADB_PRE = []
        file_name = None
        if self.args.android_command:
            ADB_SHELL_STEPS = self.args.android_command
            cmds_str = ','.join(ADB_SHELL_STEPS)
            if len(cmds_str) > 40:
                cmds_str = '%s...' % (cmds_str[:40])
            test_name_suffix = 'command=[%s]' % (cmds_str)
        elif self.args.command_file:
            file_url = self.args.command_file
            urlpath = urlparse.urlsplit(file_url).path
            file_name = os.path.basename(urlpath)
            target_path = os.path.join(config.installdir_android,
                                     test_name, file_name)
            STEPS_HOST_PRE = ["wget %s -O %s" % (file_url, file_name)]
            STEPS_ADB_PRE = ["push %s %s" % (file_name, target_path)]
            ADB_SHELL_STEPS = ["chmod 777 %s" % target_path,
                               target_path]
            file_name_str = file_name
            if len(file_name_str) > 40:
                file_name_str = '%s...' % (cmds_str[:40])
            test_name_suffix = 'command_file=%s' % (file_name_str)

        PATTERN = None
        if self.args.parse_regex:
            PATTERN = self.args.parse_regex

        tip_msg = ''
        if self.args.serial:
            tip_msg = ("Run following custom test(s) on device(%s):"
                       "\n\tcommands=%s"
                       "\n\tcommand-file=%s\n") % (
                       self.args.serial,
                       '\n\t\t'.join(ADB_SHELL_STEPS),
                       file_name)
        else:
            tip_msg = ("Run following custom test(s):"
                       "\n\t\tcommands=%s"
                       "\n\tcommand-file=%s\n") % (
                       '\n\t\t'.join(ADB_SHELL_STEPS),
                       file_name)

        self.say_begin(tip_msg)

        inst = AndroidTestInstaller()

        run = AndroidTestRunner(steps_host_pre=STEPS_HOST_PRE,
                                steps_adb_pre=STEPS_ADB_PRE,
                                adbshell_steps=ADB_SHELL_STEPS)
        parser = AndroidTestParser(pattern=PATTERN)
        test = AndroidTest(testname=test_name,
                            installer=inst, runner=run, parser=parser)
        test.parser.results = {'test_results': []}
        test.setadb(self.adb)

        if not self.test_installed(test.testname):
            test.install()

        try:
            result_id = test.run(quiet=self.args.quiet)
            if self.args.output:
                output_dir = os.path.dirname(self.args.output)
                if output_dir and (not os.path.exists(output_dir)):
                    os.makedirs(output_dir)
                bundle = generate_bundle(self.args.serial,
                        result_id, test=test,
                        test_id='%s(%s)' % (test_name, test_name_suffix))
                with open(self.args.output, "wt") as stream:
                    DocumentIO.dump(stream, bundle)

        except Exception as strerror:
            raise LavaCommandError("Test execution error: %s" % strerror)
        self.say_end(tip_msg)


class parse(AndroidResultsCommand):
    """
    Parse the results of previous test that run on the specified device
    program:: lava-android-test parse test-result-id
    """
    def invoke_sub(self):
        bundle = generate_combined_bundle(self.args.serial,
                                          self.args.result_id)
        try:
            print DocumentIO.dumps(bundle)
        except IOError:
            pass


class parse_custom(AndroidResultsCommand):
    """
    Parse the results of previous test that run with run-custom command
    on the specified device
    program:: lava-android-test parse-custom test-result-id -P
    """
    @classmethod
    def register_arguments(cls, parser):
        super(parse_custom, cls).register_arguments(parser)
        parser.add_argument('-p', '--parse-regex',
                            help=("Specified the regular expression used"
                                  " for analyzing command output"))

    def invoke_sub(self):
        PATTERN = None
        if self.args.parse_regex:
            PATTERN = self.args.parse_regex
        test_name = 'custom'
        inst = AndroidTestInstaller()
        run = AndroidTestRunner()
        parser = AndroidTestParser(pattern=PATTERN)
        test = AndroidTest(testname=test_name, installer=inst,
                                runner=run, parser=parser)
        test.parser.results = {'test_results': []}
        test.setadb(self.adb)

        bundle = generate_combined_bundle(self.args.serial,
                                          self.args.result_id, test=test)
        try:
            print DocumentIO.dumps(bundle)
        except IOError:
            pass


def generate_combined_bundle(serial=None, result_ids=None, test=None,
                             test_id=None):
    if result_ids is None:
        return {}

    bundle = None

    for rid in result_ids:
        b = generate_bundle(serial, rid, test, test_id)
        if rid == result_ids[0]:
            bundle = b
        else:
            bundle['test_runs'].append(b['test_runs'][0])

    return bundle


def generate_bundle(serial=None, result_id=None, test=None, test_id=None):
    if result_id is None:
        return {}
    config = get_config()
    adb = ADB(serial)
    resultdir = os.path.join(config.resultsdir_android, result_id)
    if not adb.exists(resultdir):
        raise  LavaCommandError("The result (%s) is not existed." % result_id)

    bundle_text = adb.read_file(os.path.join(resultdir, "testdata.json"))
    bundle = DocumentIO.loads(bundle_text)[1]
    test_tmp = None
    if bundle['test_runs'][0]['test_id'] == 'custom':
        test_tmp = test
    else:
        test_tmp = testloader(bundle['test_runs'][0]['test_id'], serial)

    if test_id:
        bundle['test_runs'][0]['test_id'] = test_id

    test_tmp.parse(result_id)
    stdout_text = adb.read_file(os.path.join(resultdir,
                                  os.path.basename(test_tmp.org_ouput_file)))
    if stdout_text is None:
        stdout_text = ''
    stderr_text = adb.read_file(os.path.join(resultdir, 'stderr.log'))
    if stderr_text is None:
        stderr_text = ''
    bundle['test_runs'][0]["test_results"] = test_tmp.parser.results[
                                                        "test_results"]
    bundle['test_runs'][0]["attachments"] = [
        {
            "pathname": test_tmp.org_ouput_file,
            "mime_type": "text/plain",
            "content":  base64.standard_b64encode(stdout_text)
        },
        {
            "pathname": 'stderr.log',
            "mime_type": "text/plain",
            "content":  base64.standard_b64encode(stderr_text)
        }
    ]
    screencap_path = os.path.join(resultdir, 'screencap.png')
    if adb.exists(screencap_path):
        tmp_path = os.path.join(config.tempdir_host, 'screencap.png')
        adb.pull(screencap_path, tmp_path)
        with open(tmp_path, 'rb') as stream:
            data = stream.read()
        if data:
            bundle['test_runs'][0]["attachments"].append({
            "pathname": 'screencap.png',
            "mime_type": 'image/png',
            "content": base64.standard_b64encode(data)})

    return bundle


class show(AndroidResultCommand):
    """
    Display the output from a previous test that run on the specified device
    program:: lava-android-test show result-id
    program:: lava-android-test show result-id -s device_serial
    """
    def invoke_sub(self):
        resultsdir = os.path.join(self.config.resultsdir_android,
                                   self.args.result_id)
        if not self.adb.exists(resultsdir):
            raise  LavaCommandError(
                    "The result (%s) is not existed." % self.args.result_id)

        stdout = os.path.join(resultsdir, "stdout.log")
        if not self.adb.exists(stdout):
            self.say("No result found for '%s'" % self.args.result_id)
            return
        try:
            output = self.adb.get_shellcmdoutput('cat %s' % stdout)[1]
            if output is not None:
                for line in output:
                    self.display_subprocess_output('stdout', line)
        except IOError:
            pass

        stderr = os.path.join(resultsdir, "stderr.log")
        if not self.adb.exists(stderr):
            return
        try:
            output = self.adb.get_shellcmdoutput('cat %s' % stderr)[1]
            if output is not None:
                for line in output:
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

    def invoke_sub(self):
        srcdir = os.path.join(self.config.resultsdir_android,
                               self.args.result_id)
        destdir = os.path.join(self.config.resultsdir_android,
                                self.args.result_id_new)

        if not self.adb.exists(srcdir):
            self.say("Result (%s) not found" % self.args.result_id)
            return
        if self.adb.exists(destdir):
            self.say("Destination result name already exists")
        self.adb.move(srcdir, destdir)


class remove(AndroidResultsCommand):
    """
    Remove the result of a previous test that run on the specified device
    program:: lava-android-test remove result-id
    program:: lava-android-test remove result-id0 result-id1
    program:: lava-android-test remove result-id -s device_serial
    """

    @classmethod
    def register_arguments(self, parser):
        super(remove, self).register_arguments(parser)
        group = parser.add_argument_group("force to remove")
        group.add_argument("-f", "--force",
                            action="store_true",
                            help=("give an interactive question about remove"))

    def remove(self, rid):
        resultsdir = os.path.join(self.config.resultsdir_android, rid)
        if not self.adb.exists(resultsdir):
            self.say("No result found for '%s'" % rid)
            return
        if not self.args.force:
            self.say("Remove result '%s' for good? [Y/N]" % rid)
            response = raw_input()
            if response[0].upper() != 'Y':
                return
        self.adb.rmtree(resultsdir)

    def invoke_sub(self):
        for rid in self.args.result_id:
            self.remove(rid)

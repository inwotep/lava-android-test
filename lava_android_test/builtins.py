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
from optparse import make_option
from lava_android_test.adb import ADB
from lava_android_test.config import get_config
from lava_android_test.command import AndroidTestCmd, get_command, get_all_cmds
from lava_android_test.testdef import testloader


class cmd_version(AndroidTestCmd):
    """
    Show the version of AndroidTestCmd
    """
    def run(self):
        import lava_android_test
        print lava_android_test.__version__


class cmd_help(AndroidTestCmd):
    """ Get help on AndroidTestCmd commands

    If the command name is ommited, calling the help command will return a
    list of valid commands.
    """
    arglist = ['command', 'subcommand']
    def run(self):
        if len(self.args) < 1:
            print "Available commands:"
            for cmd in get_all_cmds():
                print "  %s" % cmd
            print
            print "To access extended help on a command use 'abrek help " \
                  "[command]'"
            return
        command_name = self.args.pop(0)
        cmd = get_command(command_name)
        if not cmd:
            print "No command found for '%s'" % command_name
            return
        while self.args:
            subcommand_name = self.args.pop(0)
            cmd = cmd.get_subcommand(subcommand_name)
            if not cmd:
                print "No sub-command of '%s' found for '%s'" % (
                    command_name, subcommand_name)
                return
            command_name += ' ' + subcommand_name
        print cmd.help()


class cmd_install(AndroidTestCmd):
    """
    Install a test to android
    """
    options = [make_option("-s", "--serial", dest="serial")]
    arglist = ['*testname']

    def run(self):
        #TODO need to check whether the device is connected
        if len(self.args) != 1:
            print "please specify the name of the test to install"
            sys.exit(1)
        test = testloader(self.args[0], self.opts.serial)
        try:
            test.install()
        except RuntimeError as strerror:
            print "Test installation error: %s" % strerror
            sys.exit(1)

class cmd_run(AndroidTestCmd):
    """
    Run tests
    """
    arglist = ['*testname']
    options = [make_option("-s", "--serial", dest="serial"),
               make_option('-q', '--quiet', action='store_true',
                           default=False, dest='quiet'),
               make_option('-o', '--output',  action='store',
                           default=None, metavar="FILE",
                           help="Store processed test output to FILE")]

    def run(self):
        if len(self.args) != 1:
            print "please specify the name of the test to run"
            sys.exit(1)
        test = testloader(self.args[0], self.opts.serial)
        try:
            result_id = test.run(quiet=self.opts.quiet)
            if self.opts.output:
                from lava_android_test.dashboard import generate_bundle
                import json
                bundle = generate_bundle(result_id, ADB(self.opts.serial))
                with open(self.opts.output, "wt") as stream:
                    json.dump(bundle, stream)
        except Exception as strerror:
            print "Test execution error: %s" % strerror
            sys.exit(1)


class cmd_uninstall(AndroidTestCmd):
    """
    Uninstall a test
    """
    arglist = ['*testname']
    options = [make_option("-s", "--serial", dest="serial")]

    def run(self):
        if len(self.args) != 1:
            print "please specify the name of the test to uninstall"
            sys.exit(1)
        test = testloader(self.args[0], self.opts.serial)
        try:
            test.uninstall()
        except Exception as strerror:
            print "Test uninstall error: %s" % strerror
            sys.exit(1)


class cmd_list_installed(AndroidTestCmd):
    """
    List tests that are currently installed
    """
    
    options = [make_option("-s", "--serial", dest="serial")]
    
    def run(self):
        config = get_config()
        self.adb = ADB(self.opts.serial)
        
        print "Installed tests:"
        try:
            (ret_code, output) = self.adb.listdir(config.installdir_android)
            if output is not None:
                for dir in output:
                    print dir.strip()
            else:
                print "No tests installed"
        except OSError:
            print "No tests installed"


class cmd_list_tests(AndroidTestCmd):
    """
    List all known tests
    """
    def run(self):
        from lava_android_test import test_definitions
        from pkgutil import walk_packages
        print "Known tests:"
        for importer, mod, ispkg in walk_packages(test_definitions.__path__):
            print mod


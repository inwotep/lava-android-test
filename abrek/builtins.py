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

import abrek.command
import abrek.testdef
from abrek.config import get_config


class cmd_version(abrek.command.AbrekCmd):
    """
    Show the version of abrek
    """
    def run(self):
        import abrek
        print abrek.__version__


class cmd_help(abrek.command.AbrekCmd):
    """ Get help on abrek commands

    If the command name is ommited, calling the help command will return a
    list of valid commands.
    """
    arglist = ['command', 'subcommand']
    def run(self):
        if len(self.args) < 1:
            print "Available commands:"
            for cmd in abrek.command.get_all_cmds():
                print "  %s" % cmd
            print
            print "To access extended help on a command use 'abrek help " \
                  "[command]'"
            return
        command_name = self.args.pop(0)
        cmd = abrek.command.get_command(command_name)
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


class cmd_install(abrek.command.AbrekCmd):
    """
    Install a test
    """
    arglist = ['*testname']

    def run(self):
        self.checkroot()
        if len(self.args) != 1:
            print "please specify the name of the test to install"
            sys.exit(1)
        test = abrek.testdef.testloader(self.args[0])
        try:
            test.install()
        except RuntimeError as strerror:
            print "Test installation error: %s" % strerror
            sys.exit(1)


class cmd_run(abrek.command.AbrekCmd):
    """
    Run tests
    """
    arglist = ['*testname']
    options = [make_option('-q', '--quiet', action='store_true',
                           default=False, dest='quiet'),
               make_option('-o', '--output',  action='store',
                           default=None, metavar="FILE",
                           help="Store processed test output to FILE")]

    def run(self):
        self.checkroot()
        if len(self.args) != 1:
            print "please specify the name of the test to run"
            sys.exit(1)
        test = abrek.testdef.testloader(self.args[0])
        try:
            result_id = test.run(quiet=self.opts.quiet)
            if self.opts.output:
                from abrek.dashboard import generate_bundle
                import json
                bundle = generate_bundle(result_id)
                with open(self.opts.output, "wt") as stream:
                    json.dump(bundle, stream)
        except Exception as strerror:
            print "Test execution error: %s" % strerror
            sys.exit(1)


class cmd_uninstall(abrek.command.AbrekCmd):
    """
    Uninstall a test
    """
    arglist = ['*testname']

    def run(self):
        if len(self.args) != 1:
            print "please specify the name of the test to uninstall"
            sys.exit(1)
        test = abrek.testdef.testloader(self.args[0])
        try:
            test.uninstall()
        except Exception as strerror:
            print "Test uninstall error: %s" % strerror
            sys.exit(1)


class cmd_list_installed(abrek.command.AbrekCmd):
    """
    List tests that are currently installed
    """
    def run(self):
        config = get_config()
        print "Installed tests:"
        try:
            for dir in os.listdir(config.installdir):
                print dir
        except OSError:
            print "No tests installed"


class cmd_list_tests(abrek.command.AbrekCmd):
    """
    List all known tests
    """
    def run(self):
        from abrek import test_definitions
        from pkgutil import walk_packages
        print "Known tests:"
        for importer, mod, ispkg in walk_packages(test_definitions.__path__):
            print mod


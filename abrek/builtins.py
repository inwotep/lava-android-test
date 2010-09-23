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

import json
import os
import sys
from optparse import make_option

import abrek.command
import abrek.testdef
from abrek.config import get_config
from abrek.utils import read_file


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
    arglist = ['command']
    def run(self):
        if len(self.args) != 1:
            print "Available commands:"
            for cmd in abrek.command.get_all_cmds():
                print "  %s" % cmd
            print
            print "To access extended help on a command use 'abrek help " \
                  "[command]'"
        else:
            cmd = abrek.command.get_command(self.args[0])
            if cmd:
                print cmd.help()
            else:
                print "No command found for '%s'" % self.args[0]


class cmd_install(abrek.command.AbrekCmd):
    """
    Install a test
    """
    arglist = ['*testname']

    def run(self):
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
        default=False, dest='quiet')]

    def run(self):
        if len(self.args) != 1:
            print "please specify the name of the test to run"
            sys.exit(1)
        test = abrek.testdef.testloader(self.args[0])
        try:
            test.run(quiet=self.opts.quiet)
        except Exception as strerror:
            print "Test execution error: %s" % strerror
            sys.exit(1)


class cmd_parse(abrek.command.AbrekCmd):
    def run(self):
        if len(self.args) != 1:
            print "please specify the name of the result dir"
            sys.exit(1)
        config = abrek.config.AbrekConfig()
        resultsdir = os.path.join(config.resultsdir,self.args[0])
        testdatafile = os.path.join(resultsdir,"testdata.json")
        testdata = json.loads(file(testdatafile,'r').read())
        test = abrek.testdef.testloader(testdata['test_id'])
        try:
            test.parse(self.args[0])
        except Exception as strerror:
            print "Test parse error: %s" % strerror
            sys.exit(1)
        print test.parser.results


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


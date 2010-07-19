import os
import sys
from optparse import make_option

import abrek.command
import abrek.testdef

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

    def run(self):
        if len(self.args) != 1:
            print "please specify the name of the test to run"
            sys.exit(1)
        test = abrek.testdef.testloader(self.args[0])
        try:
            test.run()
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
        from abrek.config import get_config
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

class cmd_list_results(abrek.command.AbrekCmd):
    """
    List results of previous runs
    """
    def run(self):
        from abrek.config import get_config
        config = get_config()
        print "Saved results:"
        try:
            for dir in os.listdir(config.resultsdir):
                print dir
        except OSError:
            print "No results found"

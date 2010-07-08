import os
import sys

import abrek.command
import abrek.testdef

class cmd_version(abrek.command.AbrekCmd):
    """ Show the version of abrek

    Usage:  abrek version
    """
    def run(self, argv):
        import abrek
        print abrek.__version__

class cmd_help(abrek.command.AbrekCmd):
    """ Get help on abrek commands

    Usage: abrek help [command]

    If the command name is ommited, calling the help command will return a
    list of valid commands.
    """
    def run(self, argv):
        if len(argv) != 1:
            print "Available commands:"
            for cmd in abrek.command.get_all_cmds():
                print "  %s" % cmd
            print
            print "To access extended help on a command use 'abrek help " \
                  "[command]'"
        else:
            cmd = abrek.command.get_command(argv[0])
            if cmd:
                print cmd.help()
            else:
                print "No command found for '%s'" % argv[0]

class cmd_install(abrek.command.AbrekCmd):
    """ Install a test

    Usage: abrek install TEST_NAME
    """
    def run(self, argv):
        if len(argv) != 1:
            print "please specify the name of the test to install"
            sys.exit(1)
        test = abrek.testdef.testloader(argv[0])
        try:
            test.install()
        except RuntimeError as strerror:
            print "Test installation error: %s" % strerror
            sys.exit(1)

class cmd_run(abrek.command.AbrekCmd):
    """ Run tests

    Usage: abrek run TEST_NAME
    """
    def run(self, argv):
        if len(argv) != 1:
            print "please specify the name of the test to run"
            sys.exit(1)
        test = abrek.testdef.testloader(argv[0])
        try:
            test.run()
        except Exception as strerror:
            print "Test execution error: %s" % strerror
            sys.exit(1)

class cmd_uninstall(abrek.command.AbrekCmd):
    """ Uninstall a test

    Usage: abrek uninstall TEST_NAME
    """
    def run(self, argv):
        if len(argv) != 1:
            print "please specify the name of the test to uninstall"
            sys.exit(1)
        test = abrek.testdef.testloader(argv[0])
        try:
            test.uninstall()
        except Exception as strerror:
            print "Test uninstall error: %s" % strerror
            sys.exit(1)

class cmd_list_installed(abrek.command.AbrekCmd):
    """
    List tests that are currently installed
    """
    def run(self, argv):
        from abrek.config import AbrekConfig
        config = AbrekConfig()
        print "Installed tests:"
        for dir in os.listdir(config.installdir):
            print dir


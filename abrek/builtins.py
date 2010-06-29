import sys

from abrek.command import AbrekCmd
from abrek.testdef import testloader

class cmd_version(AbrekCmd):
    def run(self, argv):
        import abrek
        print abrek.__version__

class cmd_install(AbrekCmd):
    def run(self, argv):
        if len(argv) != 1:
            print "please specify the name of the test to install"
            sys.exit(1)
        test = testloader(argv[0])
        try:
            test.install()
        except RuntimeError as strerror:
            print "Test installation error: %s" % strerror
            sys.exit(1)

class cmd_run(AbrekCmd):
    def run(self, argv):
        if len(argv) != 1:
            print "please specify the name of the test to run"
            sys.exit(1)
        test = testloader(argv[0])
        try:
            test.run()
        except Exception as strerror:
            print "Test execution error: %s" % strerror
            sys.exit(1)

class cmd_uninstall(AbrekCmd):
    def run(self, argv):
        if len(argv) != 1:
            print "please specify the name of the test to uninstall"
            sys.exit(1)
        test = testloader(argv[0])
        try:
            test.uninstall()
        except Exception as strerror:
            print "Test uninstall error: %s" % strerror
            sys.exit(1)

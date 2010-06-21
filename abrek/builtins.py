from abrek.command import AbrekCmd
from abrek.testdef import testloader

class cmd_version(AbrekCmd):
    def run(self, argv):
        import abrek
        print abrek.__version__

class cmd_install(AbrekCmd):
    def run(self, argv):
        testname = argv[0]
        test = testloader(argv[0])
        test.install()

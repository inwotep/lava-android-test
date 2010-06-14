from abrek.commands import AbrekCmd

class cmd_version(AbrekCmd):
    def run(self, argv):
        import abrek
        print abrek.__version__

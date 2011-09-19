"""
Public API for extending Abrek
"""
from abc import abstractmethod


class ITest(object):
    """
    Abrek test.

    Something that can be installed and invoked by abre.
    """

    @abstractmethod
    def install(self):
        """
        Install the test suite.

        This creates an install directory under the user's XDG_DATA_HOME
        directory to mark that the test is installed.  The installer's
        install() method is then called from this directory to complete any
        test specific install that may be needed.
        """

    @abstractmethod
    def uninstall(self):
        """
        Uninstall the test suite.

        Uninstalling just recursively removes the test specific directory under
        the user's XDG_DATA_HOME directory.  This will both mark the test as
        removed, and clean up any files that were downloaded or installed under
        that directory.  Dependencies are intentionally not removed by this.
        """

    @abstractmethod
    def run(self, quiet=False):
        # TODO: Document me
        pass

    @abstractmethod
    def parse(self, resultname):
        # TODO: Document me
        pass

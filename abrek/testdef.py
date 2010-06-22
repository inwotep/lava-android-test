import hashlib
import os
import shutil
import sys
from commands import getstatusoutput

import abrek.config
from abrek.utils import geturl

class AbrekTest(object):
    """
    This can be used by test definition files to create an object that
    contains the building blocks for installing tests, running them,
    and parsing the results.

    testname - name of the test or test suite
    version - version of the test or test suite
    installer - AbrekInstaller instance to use
    runner - AbrekRunner instance to use
    parser - AbrekParser instance to use
    """

    def __init__(self, testname, version="", installer=None, runner=None,
                 parser=None):
        self.config = abrek.config.AbrekConfig()
        self.testname = testname
        self.version = version
        self.installer = installer
        self.runner = runner
        self.parser = parser
        self.origdir = os.path.abspath(os.curdir)

    def install(self):
        """
        Install the test suite.  This creates an install directory under
        the user's XDG_DATA_HOME directory to mark that the test is installed.
        The installer's install() method is then called from this directory
        to complete any test specific install that may be needed.
        """
        if self.installer:
            path = os.path.join(self.config.installdir, self.testname)
            if os.path.exists(path):
                raise RuntimeError, "%s is already installed" % self.testname
            os.makedirs(path)
            os.chdir(path)
            rc = self.installer.install()
            if rc:
                self.uninstall()
                raise RuntimeError, "An error was detected during", \
                                    "installation, cleaning up"

    def uninstall(self):
        """
        Uninstalling just recursively removes the test specific directory
        under the user's XDG_DATA_HOME directory.  This will both mark
        the test as removed, and clean up any files that were downloaded
        or installed under that directory.  Dependencies are intentionally
        not removed by this.
        """
        os.chdir(self.origdir)
        path = os.path.join(self.config.installdir, self.testname)
        if os.path.exists(path):
            shutil.rmtree(path)

    def run(self):
        if self.runner:
            return self.runner.run()

    def parse(self,results):
        if self.parser:
            return self.parser.parse(results)

class AbrekTestInstaller(object):
    """
    Base class for defining an installer object.  This class can be used
    as-is for simple installers, or extended for more advanced funcionality.

    steps - list of steps to be executed in a shell
    deps - list of dependencies to apt-get install before running the steps
    url - location from which the test suite should be downloaded
    md5 - md5sum to check the integrety of the download
    """

    def __init__(self, steps=[], deps=[], url="", md5="", **kwargs):
        self.steps = steps
        self.deps = deps
        self.url = url
        self.md5 = md5

    def _installdeps(self):
        if not self.deps:
            return 0
        cmd = "sudo apt-get install %s", " ".join(self.deps)
        rc,output = getstatusoutput(cmd)
        if rc:
            raise RuntimeError, "Dependency installation failed"

    def _download(self):
        """
        Download the file specified by the url and check the md5.
        Return the path and filename if successful, otherwise return None
        """
        if not self.url:
            return 0
        filename = geturl(self.url)
        #If the file does not exist, then the download was not successful
        if not os.path.exists(filename):
            return None
        if self.md5:
            checkmd5 = hashlib.md5(file(filename).read()).hexdigest()
            if checkmd5 != self.md5:
                print "ERROR: unexpected md5sum downloading %s" % filename
                return None
        return filename

    def _runsteps(self):
        for cmd in self.steps:
            rc,output = getstatusoutput(cmd)

    def install(self):
        self._installdeps()
        self._download()
        self._runsteps()

def testloader(testname):
    """
    Load the test definition, which can be either an individual
    file, or a directory with an __init__.py
    """
    importpath = "abrek.test_definitions.%s" % testname
    try:
        mod = __import__(importpath)
    except ImportError:
        print "unknown test '%s'" % testname
        sys.exit(1)
    for i in importpath.split('.')[1:]:
        mod = getattr(mod,i)
    try:
        base = mod.testdir.testobj
    except AttributeError:
        base = mod.testobj

    return base


import hashlib
import json
import os
import re
import shutil
import sys
import time
from commands import getstatusoutput
from datetime import datetime

import abrek.config
from abrek.utils import geturl, write_file

class AbrekTest(object):
    """Base class for defining tests.

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
        self.installdir = os.path.join(self.config.installdir, self.testname)
        self.origdir = os.path.abspath(os.curdir)

    def install(self):
        """Install the test suite.

        This creates an install directory under the user's XDG_DATA_HOME
        directory to mark that the test is installed.  The installer's
        install() method is then called from this directory to complete any
        test specific install that may be needed.
        """
        if not self.installer:
            raise RuntimeError("no installer defined for '%s'" %
                                self.testname)
        if os.path.exists(self.installdir):
            raise RuntimeError("%s is already installed" % self.testname)
        os.makedirs(self.installdir)
        os.chdir(self.installdir)
        try:
            self.installer.install()
        except Exception as strerror:
            self.uninstall()
            raise RuntimeError("An error was detected during",
                "installation, cleaning up: %s" % strerror)

    def uninstall(self):
        """Uninstall the test suite.

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

    def _savetestdata(self):
        testdata = {}
        filename = os.path.join(self.resultsdir, 'testdata.json')
        testdata['testname'] = self.testname
        testdata['version'] = self.version
        testdata['starttime'] = time.mktime(self.runner.starttime.timetuple())
        testdata['endtime'] = time.mktime(self.runner.endtime.timetuple())
        write_file(json.dumps(testdata), filename)

    def run(self):
        if not self.runner:
            raise RuntimeError("no test runner defined for '%s'" %
                                self.testname)
        resultname = (self.testname +
                     str(time.mktime(datetime.utcnow().timetuple())))
        self.resultsdir = os.path.join(self.config.resultsdir, resultname)
        os.makedirs(self.resultsdir)
        os.chdir(self.installdir)
        self.runner.run(self.resultsdir)
        self._savetestdata()

    def parse(self, resultname):
        if not self.parser:
            raise RuntimeError("no test parser defined for '%s'" %
                                self.testname)
        self.resultsdir = os.path.join(self.config.resultsdir, resultname)
        os.chdir(self.resultsdir)
        self.parser.parse()

class AbrekTestInstaller(object):
    """Base class for defining an installer object.
    This class can be used as-is for simple installers, or extended for more
    advanced funcionality.

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
        rc, output = getstatusoutput(cmd)
        if rc:
            raise RuntimeError("Dependency installation failed")

    def _download(self):
        """Download the file specified by the url and check the md5.

        Returns the path and filename if successful, otherwise return None
        """
        if not self.url:
            return 0
        filename = geturl(self.url)
        #If the file does not exist, then the download was not successful
        if not os.path.exists(filename):
            return None
        if self.md5:
            checkmd5 = hashlib.md5()
            with open(filename, 'rb') as fd:
                for data in fd.read(0x10000):
                    checkmd5.update(data)
            if checkmd5.hexdigest() != self.md5:
                raise RuntimeError("Unexpected md5sum downloading %s" %
                                    filename)
                return None
        return filename

    def _runsteps(self):
        for cmd in self.steps:
            rc, output = getstatusoutput(cmd)

    def install(self):
        self._installdeps()
        self._download()
        self._runsteps()

class AbrekTestRunner(object):
    """Base class for defining an test runner object.

    This class can be used as-is for simple execution with the expectation
    that the run() method will be called from the directory where the test
    was installed.  Steps, if used, should handle changing directories from
    there to the directory where the test was extracted if necessary.
    This class can also be extended for more advanced funcionality.

    steps - list of steps to be executed in a shell
    """
    def __init__(self, steps=[]):
        self.steps = steps
        self.testoutput = []

    def _runsteps(self, resultsdir):
        outputlog = os.path.join(resultsdir, 'testoutput.log')
        with open(outputlog, 'a') as fd:
            for cmd in self.steps:
                rc, output = getstatusoutput(cmd)
                fd.write(output)

    def run(self, resultsdir):
        self.starttime = datetime.utcnow()
        self._runsteps(resultsdir)
        self.endtime = datetime.utcnow()

class AbrekTestParser(object):
    """
    assume we start in the directory with test result
    init can maybe open the file? or maybe parse can do it using 'with'?
    parse() parses the file, can take a single arg of the regexp (optional?)
    has helper methods, idea is that for most things you'll likely want to
       overload the parse() method
    maybe parse could return the json string?
    """
    def __init__(self, pattern=None, fixupdict=None):
        self.pattern = pattern
        self.fixupdict = fixupdict
        self.results = {'testlist':[]}

    def _find_testid(self, id):
        for x in self.results['testlist']:
            if x['testid'] == id:
                return self.results['testlist'].index(x)

    def parse(self):
        """
        pattern - the regexp str
        """
        filename = "testoutput.log"
        pat = re.compile(self.pattern)
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                match = pat.search(line)
                if match:
                    self.results['testlist'].append(match.groupdict())
        if self.fixupdict:
            self.fixresults()

    def append(self,testid,entry):
        """
        This lets you add a dict to the entry for a specific testid
        entry should be a dict, updates it in place
        """
        index = self._find_testid(testid)
        self.results['testlist'][index].update(entry)

    def appendtoall(self,entry):
        """Append entry to each item in the testlist.

        entry - dict of key,value pairs to add to each item in the testlist
        """
        for t in self.results['testlist']:
            t.update(entry)

    def fixresults(self,fixupdict):
        """Convert results to a known, standard format

        pass it a dict of keys/values to replace
        For instance:
            {"TPASS":"pass", "TFAIL":"fail"}
        This is really only used for qualitative tests
        """
        for t in self.results['testlist']:
            if t.has_key("result"):
                t['result'] = fixupdict[t['result']]


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


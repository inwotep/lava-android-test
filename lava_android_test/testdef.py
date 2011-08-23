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

import hashlib
import os
import re
import sys
import time
from commands import getstatusoutput
from datetime import datetime
from uuid import uuid4

from lava_android_test.adb import ADB
from lava_android_test.api import ITest
from lava_android_test.config import get_config
from lava_android_test.utils import write_file, geturl
from lava_android_test import hwprofile, swprofile
from lava_android_test.bundle import DocumentIO


class AndroidTest(ITest):
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
    adb = ADB()
    
    def setadb(self, adb=None):
        self.adb = adb
        
    def getadb(self):
        return self.adb
    
    def __init__(self, testname, version="", installer=None, runner=None,
                 parser=None):
        self.testname = testname
        self.version = version
        self.installer = installer
        self.runner = runner
        self.parser = parser
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
        self.installer.setadb(self.adb)
        config = get_config()
        installdir = os.path.join(config.installdir_android, self.testname)
        if self.adb.exists(installdir):
            raise RuntimeError("%s is already installed" % self.testname)
        self.adb.makedirs(installdir)
        try:
            self.installer.install()
        except Exception :
            self.uninstall()
            raise

    def uninstall(self):
        """Uninstall the test suite.

        Uninstalling just recursively removes the test specific directory
        under the user's XDG_DATA_HOME directory.  This will both mark
        the test as removed, and clean up any files that were downloaded
        or installed under that directory.  Dependencies are intentionally
        not removed by this.
        """
        config = get_config()
        path = os.path.join(config.installdir_android, self.testname)
        if self.adb.exists(path):
            self.adb.rmtree(path)

    def _savetestdata(self, analyzer_assigned_uuid):
        TIMEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
        bundle = {
            'format': 'Dashboard Bundle Format 1.2',
            'test_runs': [
                {
                    'test_id': self.testname,
                    'analyzer_assigned_date': self.runner.starttime.strftime(TIMEFORMAT),
                    'analyzer_assigned_uuid': analyzer_assigned_uuid,
                    'time_check_performed': False,
                    'hardware_context': hwprofile.get_hardware_context(),
                    'software_context': swprofile.get_software_context(),
                }
            ]
        }
        config = get_config()
        filename_host = os.path.join(config.tempdir_host, 'testdata.json')
        write_file(DocumentIO.dumps(bundle), filename_host)
        filename_target = os.path.join(self.resultsdir, 'testdata.json')
        self.adb.push(filename_host, filename_target)

    def run(self, quiet=False):
        if not self.runner:
            raise RuntimeError("no test runner defined for '%s'" %
                                self.testname)
        config = get_config()
        resultname = (self.testname +
                     str(time.mktime(datetime.utcnow().timetuple())))
        self.resultsdir = os.path.join(config.resultsdir_andorid, resultname)
        self.adb.makedirs(self.resultsdir)
        self.runner.run(self.resultsdir)
        self._savetestdata( str(uuid4()))
        result_id = os.path.basename(self.resultsdir)
        print("ANDROID TEST RUN COMPLETE: Result id is '%s'" % result_id)
        return result_id

    def parse(self, resultname):
        if not self.parser:
            raise RuntimeError("no test parser defined for '%s'" %
                                self.testname)
        config = get_config()
        resultsdir = os.path.join(config.resultsdir, resultname)
        os.chdir(resultsdir)
        self.parser.parse()
        os.chdir(self.origdir)

    def _copy_result(self):
        os.chdir(self.resultsdir)
        self.runner.copy_result()
        os.chdir(self.origdir)

class AndroidTestInstaller(object):
    
    adb = ADB()
    
    """Base class for defining an installer object.

    This class can be used as-is for simple installers, or extended for more
    advanced funcionality.

    steps_host - list of steps to be executed on host
    steps_android - list of steps to be executed on android
    url - location from which the test suite should be downloaded
    md5 - md5sum to check the integrety of the download
    """
    def __init__(self, steps_host=[], steps_android=[], apks=[],url="", md5="", **kwargs):
        self.steps_host = steps_host
        self.steps_android = steps_android
        self.url = url
        self.md5 = md5
        self.apks = apks

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
                data = fd.read(0x10000)
                while data:
                    checkmd5.update(data)
                    data = fd.read(0x10000)
            if checkmd5.hexdigest() != self.md5:
                raise RuntimeError("Unexpected md5sum downloading %s" %
                                    filename)
                return None
        return filename

    def _runsteps_host(self):
        for cmd in self.steps_host:
            rc, output = getstatusoutput(cmd)
            if rc:
                raise RuntimeError("Run step '%s' failed. %d : %s" %(cmd,rc,output))
            
    def _runsteps_android(self):
        for cmd in self.steps_android:
            rc = self.adb.shell(cmd)
            if rc:
                raise RuntimeError("Run step '%s' failed. %d" %(cmd,rc))
    def _installapk(self):
        for apk in self.apks:
            rc = self.adb.installapk(apk)
            if rc:
                raise RuntimeError("Failed to install apk '%s' failed. %d" %(apk,rc))

    def install(self):
        self._download()
        self._runsteps_host()
        self._installapk()
        self._runsteps_android()

    def setadb(self, adb=None):
        self.adb = adb

class AndroidTestRunner(object):
    
    adb = ADB()
    """Base class for defining an test runner object.

    This class can be used as-is for simple execution with the expectation
    that the run() method will be called from the directory where the test
    was installed.  Steps, if used, should handle changing directories from
    there to the directory where the test was extracted if necessary.
    This class can also be extended for more advanced funcionality.

    steps - list of steps to be executed in a shell
    """
    def __init__(self, adbshell_steps=[], copysteps=[]):
        self.adbshell_steps = adbshell_steps
        self.copysteps = copysteps
        self.testoutput = []

    def _runsteps(self, resultsdir):
        outputlog = os.path.join(resultsdir, 'testoutput.log')
        for cmd in self.adbshell_steps:
            ret_code = self.adb.shell(cmd, outputlog)
            if ret_code != 0:
                break
        
        propoutputlog=os.path.join(resultsdir, 'propoutput.log')
        self.adb.shell('getprop', propoutputlog)
        self.adb.shell('cat /proc/cpuinfo', os.path.join(resultsdir, 'cpuinfo.log'))
        self.adb.shell('cat /proc/meminfo', os.path.join(resultsdir, 'meminfo.log'))

    def run(self, resultsdir):
        self.starttime = datetime.utcnow()
        self._runsteps(resultsdir)
        self.endtime = datetime.utcnow()

    def copy_result(self):
        """execute the copy commands in resultsdir
        """
        for cmd in self.copysteps:
            rc, output = getstatusoutput(cmd)
            if rc:
                raise RuntimeError("Run step '%s' failed. %d : %s" %(cmd,rc,output))
            
    def setadb(self, adb=None):
        self.adb = adb
    
class AndroidTestParser(object):
    adb = ADB()
    """Base class for defining a test parser

    This class can be used as-is for simple results parsers, but will
    likely need to be extended slightly for many.  If used as it is,
    the parse() method should be called while already in the results
    directory and assumes that a file for test output will exist called
    testoutput.log.

    pattern - regexp pattern to identify important elements of test output
        For example: If your testoutput had lines that look like:
            "test01:  PASS", then you could use a pattern like this:
            "^(?P<testid>\w+):\W+(?P<result>\w+)"
            This would result in identifying "test01" as testid and
            "PASS" as result.  Once parse() has been called,
            self.results.test_results[] contains a list of dicts of all the
            key,value pairs found for each test result
    fixupdict - dict of strings to convert test results to standard strings
        For example: if you want to standardize on having pass/fail results
            in lower case, but your test outputs them in upper case, you could
            use a fixupdict of something like: {'PASS':'pass','FAIL':'fail'}
    appendall - Append a dict to the test_results entry for each result.
        For example: if you would like to add units="MB/s" to each result:
            appendall={'units':'MB/s'}
    """
    def __init__(self, pattern=None, fixupdict=None, appendall={}, failure_patterns=[]):
        self.pattern = pattern
        self.fixupdict = fixupdict
        self.results = {'test_results':[]}
        self.appendall = appendall
        self.failure_patterns = failure_patterns

    def _find_testid(self, id):
        for x in self.results['test_results']:
            if x['testid'] == id:
                return self.results['test_results'].index(x)

    def parse(self):
        """Parse test output to gather results

        Use the pattern specified when the class was instantiated to look
        through the results line-by-line and find lines that match it.
        Results are then stored in self.results.  If a fixupdict was supplied
        it is used to convert test result strings to a standard format.
        """
        filename = "testoutput.log"
        try:
           pat = re.compile(self.pattern)
        except Exception as strerror:
            raise RuntimeError(
                "AbrekTestParser - Invalid regular expression '%s' - %s" % (
                    self.pattern,strerror))
            
        failure_pats = []
        for failure_pattern in self.failure_patterns:
            try:
                failure_pat = re.compile(failure_pattern)
            except Exception as strerror:
                raise RuntimeError(
                    "AbrekTestParser - Invalid regular expression '%s' - %s" % (
                        failure_pattern, strerror))
            failure_pats.append(failure_pat)
        test_ok = True
        with open(filename, 'r') as stream:
            for lineno, line in enumerate(stream, 1):
                if test_ok == True:
                   for failure_pat in failure_pats:
                        failure_match = failure_pat.search(line)
                        if failure_match:
                            test_ok = False

        with open(filename, 'r') as stream:
            for lineno, line in enumerate(stream, 1):
                match = pat.search(line)
                if not match:
                    continue
                data = match.groupdict()
                data["log_filename"] = filename
                data["log_lineno"] = lineno
                data['result'] = test_ok
                self.results['test_results'].append(data)
        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()
        self.fixids()

    def append(self, testid, entry):
        """Appends a dict to the test_results entry for a specified testid

        This lets you add a dict to the entry for a specific testid
        entry should be a dict, updates it in place
        """
        index = self._find_testid(testid)
        self.results['test_results'][index].update(entry)

    def appendtoall(self, entry):
        """Append entry to each item in the test_results.

        entry - dict of key,value pairs to add to each item in the
        test_results
        """
        for t in self.results['test_results']:
            t.update(entry)

    def fixresults(self, fixupdict):
        """Convert results to a known, standard format

        pass it a dict of keys/values to replace
        For instance:
            {"TPASS":"pass", "TFAIL":"fail"}
        This is really only used for qualitative tests
        """
        for t in self.results['test_results']:
            if t.has_key("result"):
                t['result'] = fixupdict[t['result']]

    def fixmeasurements(self):
        """Measurements are often read as strings, but need to be float
        """
        for id in self.results['test_results']:
            if id.has_key('measurement'):
                id['measurement'] = float(id['measurement'])

    def fixids(self):
        """
        Convert spaces to _ in test_case_id and remove illegal characters
        """
        badchars = "[^a-zA-Z0-9\._-]"
        for id in self.results['test_results']:
            if id.has_key('test_case_id'):
                id['test_case_id'] = id['test_case_id'].replace(" ", "_")
                id['test_case_id'] = re.sub(badchars, "", id['test_case_id'])
            
    def setadb(self, adb=None):
        self.adb = adb

def testloader(testname, serial=None):
    """
    Load the test definition, which can be either an individual
    file, or a directory with an __init__.py
    """
    importpath = "lava_android_test.test_definitions.%s" % testname
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
    
    base.setadb(ADB(serial))
    return base


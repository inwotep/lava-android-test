# Copyright (C) 2010-2012 Linaro Limited
#
# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.

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

import base64
import hashlib
import logging
import os
import re
import string
import time
import tempfile
import decimal
import zipfile

from datetime import datetime
from uuid import uuid4

from lava_android_test.adb import ADB
from lava_android_test.api import ITest
from lava_android_test.config import get_config
from lava_android_test.utils import write_file, geturl
from lava_android_test import hwprofile, swprofile
from linaro_dashboard_bundle.io import DocumentIO


class Attachment(object):

    def __init__(self, pathname=None, mime_type=None):
        self.pathname = pathname
        self.mime_type = mime_type

    def copy_to_result_dir(self, adb=None, resultsdir=None):
        """
        Copy the file specified by the pathname to result
        directory of this time test, beacuse some test will
        generate the result to the same path file.
        And Please Note that pathname must be the absolute
        path in the device.
        """
        if (not self.pathname) or (not self.pathname.startswith('/')):
            return
        if not resultsdir:
            return
        if not adb:
            adb = ADB()
        if not adb.exists(resultsdir):
            adb.makedirs(resultsdir)
        ret_code = adb.copy(self.pathname, os.path.join(resultsdir,
                                     os.path.basename(self.pathname)))
        if ret_code != 0:
            raise RuntimeError(
                    "Failed to copy file '%s' to '%s' on device(%s)" %
                        (self.pathname, resultsdir, adb.get_serial()))

    def generate_bundle(self, adb=None, resultsdir=None):
        data_bundle = {}
        if not self.pathname:
            return data_bundle
        if not adb:
            adb = ADB()
        config = get_config()
        basename = os.path.basename(self.pathname)
        android_path = os.path.join(resultsdir, basename)
        if adb.exists(android_path):
            tmp_path = os.path.join(config.tempdir_host, basename)
            adb.pull(android_path, tmp_path)
            with open(tmp_path, 'rb') as stream:
                data = stream.read()
            if data:
                data_bundle = {"pathname": basename,
                               "mime_type": self.mime_type,
                               "content": base64.standard_b64encode(data)}
            os.unlink(tmp_path)
        return data_bundle


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
    default_attachments = [
        Attachment(pathname="stderr.log", mime_type="text/plain"),
        Attachment(pathname="stdout.log", mime_type="text/plain"),
        Attachment(pathname="screencap.png", mime_type="image/png"),
        Attachment(pathname="tombstones.zip", mime_type="application/zip")
        ]

    def setadb(self, adb=None):
        self.adb = adb

    def getadb(self):
        return self.adb

    def __init__(self, testname, version="", installer=None, runner=None,
                 parser=None, default_options=None,
                 org_ouput_file='stdout.log',
                 attachments=[]):
        self.testname = testname
        self.version = version
        self.installer = installer
        self.runner = runner
        self.parser = parser
        self.default_options = default_options
        self.org_ouput_file = org_ouput_file
        self.origdir = os.path.abspath(os.curdir)
        self.attachments = self.default_attachments
        if self.org_ouput_file and (self.org_ouput_file != "stdout.log"):
            self.attachments.append(
                Attachment(pathname=self.org_ouput_file,
                           mime_type="text/plain"))
        if attachments:
            self.attachments.extend(attachments)

    def set_runner(self, runner=None):
        self.runner = runner

    def set_parser(self, parser=None):
        self.parser = parser

    def install(self, install_options=None):
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
        if not os.path.exists(config.tempdir_host):
            os.makedirs(config.tempdir_host)
        os.chdir(config.tempdir_host)
        installdir = os.path.join(config.installdir_android, self.testname)
        if self.adb.exists(installdir):
            raise RuntimeError("%s is already installed" % self.testname)
        ret_code = self.adb.makedirs(installdir)
        if ret_code != 0:
            raise RuntimeError(
                               "Failed to create directory(%s) for test(%s)" %
                               (installdir, self.testname))

        if install_options is not None:
            self.adb.shell('echo "%s" > %s/install_options' %
                           (install_options, installdir))
        try:
            self.installer.install(install_options)
        except Exception as e:
            self.uninstall()
            raise RuntimeError(
                    "Failed to install test(%s):%s" % (self.testname, e))
        finally:
            os.chdir(self.origdir)

    def uninstall(self):
        """Uninstall the test suite.

        Uninstalling just recursively removes the test specific directory
        under the user's XDG_DATA_HOME directory.  This will both mark
        the test as removed, and clean up any files that were downloaded
        or installed under that directory.  Dependencies are intentionally
        not removed by this. And others installed files won't be removed too.
        """
        config = get_config()
        path = os.path.join(config.installdir_android, self.testname)
        if self.adb.exists(path):
            self.adb.rmtree(path)

    def _add_install_options(self, bundle, config):
        optionfile = "%s/%s/install_options" % (config.installdir_android,
                                                self.testname)
        if self.adb.exists(optionfile):
            output = self.adb.run_adb_cmd('shell cat %s' % optionfile)[1]
            bundle['test_runs'][0]['attributes']['install_options'] = output[0]

    def _savetestdata(self, analyzer_assigned_uuid, run_options=""):
        config = get_config()
        TIMEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
        bundle = {
            'format': config.bundle_format,
            'test_runs': [
                {
                'analyzer_assigned_uuid': analyzer_assigned_uuid,
                'analyzer_assigned_date':
                        self.runner.starttime.strftime(TIMEFORMAT),
                'time_check_performed': False,
                'attributes':{},
                'test_id': self.testname,
                'test_results':[],
                'attachments':[],
                'hardware_context': hwprofile.get_hardware_context(self.adb),
                'software_context': swprofile.get_software_context(self.adb)
                }
            ]
        }
        if run_options:
            bundle['test_runs'][0]['attributes']['run_options'] = run_options
        self._add_install_options(bundle, config)
        filename_host = os.path.join(config.tempdir_host, 'testdata.json')
        write_file(DocumentIO.dumps(bundle), filename_host)
        filename_target = os.path.join(self.resultsdir, 'testdata.json')
        self.adb.push(filename_host, filename_target)

    def run(self, quiet=False, run_options=None):
        if not self.runner:
            raise RuntimeError("no test runner defined for '%s'" %
                                self.testname)
        if not run_options:
            run_options = self.default_options

        self.runner.setadb(self.adb)
        config = get_config()
        if not os.path.exists(config.tempdir_host):
            os.mkdir(config.tempdir_host)
        os.chdir(config.tempdir_host)
        resultname = (self.testname +
                     str(time.mktime(datetime.utcnow().timetuple())))
        self.resultsdir = os.path.join(config.resultsdir_android, resultname)
        self.adb.makedirs(self.resultsdir)
        self.runner.run(self.resultsdir, run_options=run_options)
        self._gather_tombstones(self.resultsdir)
        self._copyattachments(self.resultsdir)
        self._screencap(self.resultsdir)
        self._savetestdata(str(uuid4()), run_options=run_options)
        result_id = os.path.basename(self.resultsdir)
        print("ANDROID TEST RUN COMPLETE: Result id is '%s'" % result_id)
        os.chdir(self.origdir)
        return result_id

    def _screencap(self, resultsdir):
        target_path = '/system/bin/screenshot'
        self.adb.shell('%s %s' % (target_path, os.path.join(resultsdir,
                                                        'screencap.png')))

    def _gather_tombstones(self, resultsdir):
        """
        Extension of the generate bundle function.
        Grabs the tombstones and appends them to the bundle.
        """
        config = get_config()
        tombstone_path = '/data/tombstones'
        tombstone_zip = os.path.join(config.tempdir_host, 'tombstones.zip')
        if self.adb.exists(tombstone_path):
            tmp_path = os.path.join(config.tempdir_host, 'tombstones')
            self.adb.pull(tombstone_path, tmp_path)
            self.adb.shell("rm -R " + tombstone_path)
            zipf = zipfile.ZipFile(tombstone_zip, mode='w')
            for rootdir, dirs, files in os.walk(tmp_path):
                for f in files:
                    zipf.write(os.path.join(rootdir, f), arcname=f)
            zipf.close()
            self.adb.push(tombstone_zip, os.path.join(resultsdir,
                                                      'tombstones.zip'))
            os.unlink(tombstone_zip)

    def _copyattachments(self, resultsdir):
        for attachment in self.attachments:
            attachment.copy_to_result_dir(adb=self.adb, resultsdir=resultsdir)

    def parse(self, resultname):
        if not self.parser:
            raise RuntimeError("no test parser defined for '%s'" %
                                self.testname)
        output_filename = os.path.basename(self.org_ouput_file)
        config = get_config()
        os.chdir(config.tempdir_host)
        resultsdir_android = os.path.join(config.resultsdir_android,
                                           resultname)
        result_filename_android = os.path.join(resultsdir_android,
                                               output_filename)
        result_filename_host_temp = tempfile.mkstemp(prefix=output_filename,
                                                dir=config.tempdir_host)[1]
        self.adb.pull(result_filename_android, result_filename_host_temp)
        self.parser.parse(output_filename,
                          output_filename=result_filename_host_temp,
                          test_name=self.testname)
        os.remove(result_filename_host_temp)
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
    def __init__(self, steps_host_pre=[], steps_adb_pre=[], apks=[],
                 steps_adb_post=[], steps_host_post=[],
                  url=None, md5=None, **kwargs):
        self.steps_host_pre = steps_host_pre
        self.steps_adb_pre = steps_adb_pre
        self.apks = apks
        self.steps_adb_post = steps_adb_post
        self.steps_host_post = steps_host_post
        self.url = url
        self.md5 = md5

    def _download(self):
        """Download the file specified by the url and check the md5.
        Returns the path and filename if successful, otherwise return None
        """
        if not self.url:
            return 0
        config = get_config()
        filename = geturl(self.url, config.tempdir_host)
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

    def _installapk(self):
        for apk in self.apks:
            rc = self.adb.installapk(apk)
            if rc:
                raise RuntimeError(
                        "Failed to install apk '%s' failed. %d" % (apk, rc))

    def install(self, install_options=None):
        self._download()
        _run_steps_host(self.steps_host_pre, self.adb.serial, install_options)
        _run_steps_adb(self.steps_adb_pre, self.adb.serial, install_options)
        self._installapk()
        _run_steps_adb(self.steps_adb_post, self.adb.serial, install_options)
        _run_steps_host(self.steps_host_post, self.adb.serial, install_options)

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
    def __init__(self, steps_host_pre=[], steps_adb_pre=[],
                 adbshell_steps=[], steps_adb_post=[], steps_host_post=[]):
        self.steps_host_pre = steps_host_pre
        self.steps_adb_pre = steps_adb_pre
        self.adbshell_steps = adbshell_steps
        self.steps_adb_post = steps_adb_post
        self.steps_host_post = steps_host_post
        self.testoutput = []

    def _run_steps_adbshell(self, resultsdir, option=None):
        stdoutlog = os.path.join(resultsdir, 'stdout.log')
        stderrlog = os.path.join(resultsdir, 'stderr.log')
        try:
            for cmd in self.adbshell_steps:
                if option is not None:
                    cmd = cmd.replace('$(OPTIONS)', option)
                else:
                    cmd = cmd.replace('$(OPTIONS)', '')
                if resultsdir is not None:
                    cmd = cmd.replace('$(RESULTDIR)', resultsdir)
                else:
                    cmd = cmd.replace('$(RESULTDIR)', '')
                cmd = cmd.strip()
                ret_code = self.adb.run_adb_shell_for_test(cmd,
                                                           stdoutlog,
                                                            stderrlog)
                if ret_code != 0:
                    raise Exception(
                        "Failed to execute command(%s):ret_code=%d" % (cmd,
                                                                     ret_code))
        except:
            raise
        finally:
            self.adb.shell('getprop',
                           os.path.join(resultsdir, 'propoutput.log'))
            self.adb.shell('cat /proc/cpuinfo',
                           os.path.join(resultsdir, 'cpuinfo.log'))
            self.adb.shell('cat /proc/meminfo',
                           os.path.join(resultsdir, 'meminfo.log'))

    def run(self, resultsdir, run_options=None):
        self.starttime = datetime.utcnow()
        _run_steps_host(self.steps_host_pre, self.adb.serial,
                        option=run_options, resultsdir=resultsdir)
        _run_steps_adb(self.steps_adb_pre, self.adb.serial,
                        option=run_options, resultsdir=resultsdir)
        self._run_steps_adbshell(resultsdir, option=run_options)
        _run_steps_adb(self.steps_adb_post, self.adb.serial,
                        option=run_options, resultsdir=resultsdir)
        _run_steps_host(self.steps_host_post, self.adb.serial,
                        option=run_options, resultsdir=resultsdir)
        self.endtime = datetime.utcnow()

    def setadb(self, adb=None):
        self.adb = adb


class AndroidTestParser(object):
    adb = ADB()
    PASS_PATS = ['PASS', 'OK', 'TRUE', 'DONE']
    FAIL_PATS = ['FAIL', 'NG', 'FALSE']
    SKIP_PATS = ['SKIP']

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
    failure_patterns - regexp pattern to identify whether the test is failed
         or success
        If there is a string match one pattern in failure_patterns,
        then this test will be deal as failed.
    """
    def __init__(self, pattern=None, fixupdict=None, appendall={},
                  failure_patterns=[]):
        self.pattern = pattern
        self.fixupdict = fixupdict
        self.results = {'test_results': []}
        self.appendall = appendall
        self.failure_patterns = failure_patterns

    def _find_testid(self, test_id):
        for x in self.results['test_results']:
            if x['testid'] == test_id:
                return self.results['test_results'].index(x)

    def parse(self, result_filename='stdout.log',
              output_filename='stdout.log', test_name=''):
        """Parse test output to gather results

        Use the pattern specified when the class was instantiated to look
        through the results line-by-line and find lines that match it.
        Results are then stored in self.results.  If a fixupdict was supplied
        it is used to convert test result strings to a standard format.
        """

        self.real_parse(result_filename=result_filename,
              output_filename=output_filename, test_name=test_name)

        self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()
        self.fixids(test_name=test_name)

    def real_parse(self, result_filename='stdout.log',
              output_filename='stdout.log', test_name=''):
        """Using the pattern to do the real parse operation

        generate the test_results elements from the result file by parsing
        with the pattern specified.
        """
        if not self.pattern:
            return

        try:
            pat = re.compile(self.pattern)
        except Exception as strerror:
            raise RuntimeError(
                "AndroidTestParser - Invalid regular expression '%s' - %s" % (
                    self.pattern, strerror))

        failure_pats = []
        for failure_pattern in self.failure_patterns:
            try:
                failure_pat = re.compile(failure_pattern)
            except Exception as strerror:
                raise RuntimeError(
                "AndroidTestParser - Invalid regular expression '%s' - %s" % (
                        failure_pattern, strerror))
            failure_pats.append(failure_pat)
        test_ok = True

        with open(output_filename, 'r') as stream:
            for lineno, line in enumerate(stream, 1):
                if test_ok == True:
                    for failure_pat in failure_pats:
                        failure_match = failure_pat.search(line)
                        if failure_match:
                            test_ok = False

                match = pat.search(line)
                if not match:
                    continue
                data = match.groupdict()
                data["log_filename"] = result_filename
                data["log_lineno"] = lineno
                if data.get('result') is None:
                    data['result'] = test_ok and 'pass' or 'fail'
                self.results['test_results'].append(data)

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
            if "result" in t:
                if not fixupdict:
                    if self.is_result_match(t['result'], self.PASS_PATS):
                        t['result'] = 'pass'
                    elif self.is_result_match(t['result'], self.FAIL_PATS):
                        t['result'] = 'fail'
                    elif self.is_result_match(t['result'], self.SKIP_PATS):
                        t['result'] = 'skip'
                    else:
                        t['result'] = 'unknown'
                elif t['result'] in fixupdict:
                    t['result'] = fixupdict[t['result']]
                else:
                    t['result'] = 'unknown'

    def is_result_match(self, result, patterns=[]):
        cap_result = string.upper(result)
        for pattern in patterns:
            cap_pattern = string.upper(pattern)
            pat_index = string.find(cap_result, cap_pattern)
            if pat_index > -1:
                return True

        return False

    def fixmeasurements(self):
        """Measurements are often read as strings, but need to be
        decimal.Decimal as per dashboard bundle format JSON schema.
        """
        for test_case in self.results['test_results']:
            if 'measurement' in test_case:
                try:
                    test_case['measurement'] = decimal.Decimal(
                        test_case['measurement'])
                except decimal.InvalidOperation:
                    logging.warning("Invalid measurement %s" % (
                            test_case['measurement']))
                    del test_case['measurement']

    def fixids(self, test_name=''):
        """
        Convert spaces to _ in test_case_id and remove illegal characters
        """
        badchars = "[^a-zA-Z0-9\._-]"
        for test_case in self.results['test_results']:
            if 'test_case_id' in test_case:
                test_case['test_case_id'] = test_case[
                                            'test_case_id'].replace(" ", "_")
                test_case['test_case_id'] = re.sub(badchars, "",
                                                    test_case['test_case_id'])
            else:
                test_case['test_case_id'] = test_name

    def setadb(self, adb=None):
        self.adb = adb

    def set_result_patterns(self, pass_pat=[], fail_pat=[], skip_pat=[]):
        if pass_pat:
            self.PASS_PATS = pass_pat
        if fail_pat:
            self.FAIL_PATS = fail_pat
        if skip_pat:
            self.SKIP_PATS = skip_pat


class AndroidInstrumentTestParser(AndroidTestParser):

    def parse(self, result_filename='stdout.log', output_filename='stdout.log',
               test_name=''):
        """Parser for Instrument test that run with the -r option
        """
        pat_test = re.compile(
            r'^\s*INSTRUMENTATION_STATUS:\s*test=(?P<test_case_id>.+)\s*$')
        pat_status_code = re.compile(
            r'^\s*INSTRUMENTATION_STATUS_CODE:\s*(?P<status_code>[\d-]+)\s*$')
        data = {}
        with open(output_filename, 'r') as stream:
            for lineno, line in enumerate(stream, 1):
                match = pat_test.search(line)
                if match:
                    data['test_case_id'] = match.group('test_case_id')
                    continue

                match = pat_status_code.search(line)
                if match:
                    status_code = match.group('status_code')
                    if status_code == '1':
                        # test case started
                        data = {}
                    elif data['test_case_id']:
                        if status_code == '0':
                            data['result'] = 'pass'
                        else:
                            data['result'] = 'fail'
                        data["log_filename"] = result_filename
                        data["log_lineno"] = lineno
                        self.results['test_results'].append(data)
                        data = {}
                    continue

        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()
        self.fixids()


class AndroidSimpleTestParser(AndroidTestParser):

    def real_parse(self, result_filename='stdout.log',
              output_filename='stdout.log', test_name=''):
        self.res_pattern = ("^\s*(?P<test_case_id>.+?)\s*="
                   "\s*(?P<result>(pass|fail|ok|ng|true|false|skip|done))\s*$")
        self.measurement_pattern = ("^\s*(?P<test_case_id>.+?)\s*="
                        "\s*(?P<measurement>[\.\d]+)\s*$")
        self.measurement_units_pattern = ("^\s*(?P<test_case_id>.+?)\s*="
                        "\s*(?P<measurement>[\.\d]+)\s+(?P<units>\S+)\s*$")

        res_pat = re.compile(self.res_pattern)
        measurement_pat = re.compile(self.measurement_pattern)
        measurement_units_pat = re.compile(self.measurement_units_pattern)

        with open(output_filename, 'r') as stream:
            for lineno, line in enumerate(stream, 1):
                match = res_pat.search(line)
                if not match:
                    match = measurement_pat.search(line)
                    if not match:
                        match = measurement_units_pat.search(line)
                        if not match:
                            continue
                data = match.groupdict()
                data["log_filename"] = result_filename
                data["log_lineno"] = lineno
                if data.get('result') is None:
                    data['result'] = 'pass'

                self.results['test_results'].append(data)


def _run_steps_host(steps=[], serial=None, option=None, resultsdir=None):
    adb = ADB(serial)
    for cmd in steps:
        if serial is not None:
            cmd = cmd.replace('$(SERIAL)', serial)
        else:
            cmd = cmd.replace('$(SERIAL)', '')
        if option is not None:
            cmd = cmd.replace('$(OPTIONS)', option)
        else:
            cmd = cmd.replace('$(OPTIONS)', '')
        if resultsdir is not None:
            cmd = cmd.replace('$(RESULTDIR)', resultsdir)
        else:
            cmd = cmd.replace('$(RESULTDIR)', '')

        cmd = cmd.strip()
        rc, output = adb.run_cmd_host(cmd, quiet=False)
        if rc:
            raise RuntimeError(
                    "Run step '%s' failed. %d : %s" % (cmd, rc, output))
        if resultsdir is not None:
            stdoutlog = os.path.join(resultsdir, 'stdout.log')
            adb.push_stream_to_device(output, stdoutlog)


def _run_steps_adb(steps=[], serial=None, option=None, resultsdir=None):
    adb = ADB(serial)
    for cmd in steps:
        if option is not None:
            cmd = cmd.replace('$(OPTIONS)', option)
        else:
            cmd = cmd.replace('$(OPTIONS)', '')
        if resultsdir is not None:
            cmd = cmd.replace('$(RESULTDIR)', resultsdir)
        else:
            cmd = cmd.replace('$(RESULTDIR)', '')
        cmd = cmd.strip()
        rc, output = adb.run_adb_cmd(cmd, quiet=False)
        if rc:
            raise RuntimeError(
                    "Run step '%s' failed. %d : %s" % (cmd, rc, output))
        if resultsdir is not None:
            stdoutlog = os.path.join(resultsdir, 'stdout.log')
            adb.push_stream_to_device(output, stdoutlog)

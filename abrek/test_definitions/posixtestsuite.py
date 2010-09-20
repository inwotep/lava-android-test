"""
   This script automates the automate installation, execution, and 
   results parsing for the OpenPosix test suite. 
   The POSIX Test Suite is an open source test suite with the goal of
   performing conformance, functional, and stress testing of the IEEE
   1003.1-2001 System Interfaces specification However the automation here 
   does not support the stress test runs.

"""
import re
import abrek.testdef

VERSION="1.5.2"
URL="http://sourceforge.net/projects/posixtest/files/posixtest/" \
    "posixtestsuite-%s/posixtestsuite-%s.tar.gz" % (VERSION, VERSION)
MD5="9a8e6516585c886fddc257270061b59c"
INSTALLSTEPS = ['tar -zxvf posixtestsuite-1.5.2.tar.gz']
RUNSTEPS = ['cd posixtestsuite && make']
PATTERN = "((?P<test_case_id>\A(\w+[/]+)+(\d+[-]\d+):) (?P<message>\D+:)" \
          " (?P<result>\D+))"
FIXUPS = {   
            "FAILED"      :  "fail",
            "INTERRUPTED" :  "skip",
            "PASS"        :  "pass",
            "UNRESOLVED"  :  "unknown",
            "UNSUPPORTED" :  "skip",
            "UNTESTED"    :  "skip",
            "SKIP"        :  "skip"
         }


class PosixParser(abrek.testdef.AbrekTestParser):
    def parse(self):
        filename = "testoutput.log"
        pat = re.compile(self.pattern)
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                match = pat.search(line)
                if match:
                    results = match.groupdict()
                    for key in results.keys():
                        results[key] = results[key].rstrip("\n")
                        results[key] = results[key].rstrip(":")
                        results[key] = results[key].rstrip()
                    test_case_id = results['test_case_id']
                    results['test_case_id'] = test_case_id.replace("/", ".")
                    self.results['test_results'].append(results)
        if self.fixupdict:
            self.fixresults(self.fixupdict)

posix_inst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, url=URL, md5=MD5)
posix_run = abrek.testdef.AbrekTestRunner(RUNSTEPS)
posixparser = PosixParser(PATTERN, fixupdict = FIXUPS)
testobj = abrek.testdef.AbrekTest(testname="posixtestsuite", version=VERSION,
                                  installer=posix_inst, runner=posix_run,
                                  parser=posixparser)

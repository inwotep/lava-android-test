import re

import abrek.testdef

VERSION="20100831"
URL='http://downloads.sourceforge.net/project/ltp/LTP Source/ltp-%s/ltp-full-%s.bz2' % (VERSION, VERSION)
#URL="http://downloads.sourceforge.net/project/ltp/LTP Source/ltp-20100831/ltp-full-20100831.bz2"
MD5="6982c72429a62f3917c13b2d529ad1ce"
DEPS = ['bzip2', 'flex', 'bison', 'make']

SCRIPT = """
tar -xjf ltp-full-20100831.bz2
mkdir build
cd ltp-full-20100831
./configure --prefix=$(readlink -f ../build)
make all
SKIP_IDCHECK=1 make install
"""

INSTALLSTEPS = ["echo '%s' > installltp.sh" % SCRIPT,
                'chmod +x installltp.sh',
                './installltp.sh']
RUNSTEPS = ['cd build && sudo ./runltp -f syscalls -p -q']
PATTERN = "^(?P<test_case_id>\S+)    (?P<subid>\d+)  (?P<result>\w+)  :  (?P<message>\S+)"
FIXUPS = {"TBROK":"fail",
          "TCONF":"skip",
          "TFAIL":"fail",
          "TINFO":"unknown",
          "TPASS":"pass",
          "TWARN":"unknown"}


class LTPParser(abrek.testdef.AbrekTestParser):
    def parse(self):
        filename = "testoutput.log"
        pat = re.compile(self.pattern)
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                match = pat.search(line)
                if match:
                    results = match.groupdict()
                    results['test_case_id'] += "." + results.pop('subid')
                    self.results['test_results'].append(results)
        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)


ltpinst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, deps=DEPS, url=URL,
                                           md5=MD5)
ltprun = abrek.testdef.AbrekTestRunner(RUNSTEPS)
ltpparser = LTPParser(PATTERN, fixupdict = FIXUPS)
testobj = abrek.testdef.AbrekTest(testname="ltp", version=VERSION,
                                  installer=ltpinst, runner=ltprun,
                                  parser=ltpparser)

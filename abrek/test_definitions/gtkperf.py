import re
import abrek.testdef

# Run tests automatically, 500 repetitions each
gtkperf_options = "-a -c 500"

RUNSTEPS = ["gtkperf %s" % gtkperf_options]

class GtkTestParser(abrek.testdef.AbrekTestParser):
    def parse(self):
        PAT1 = "^(?P<test_case_id>\w+) - (?P<subtest>\w*\W*\w*) - time:\W+(?P<measurement>\d+\.\d+)"
        PAT2 = "^(?P<test_case_id>\w+) - time:\W+(?P<measurement>\d+\.\d+)"
        filename = "testoutput.log"
        pat1 = re.compile(PAT1)
        pat2 = re.compile(PAT2)
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                match = pat1.search(line)
                if match:
                    d = match.groupdict()
                    d['test_case_id'] = "%s.%s" % (d['test_case_id'],
                        d['subtest'])
                    d.pop('subtest')
                    self.results['test_results'].append(d)
                else:
                    match = pat2.search(line)
                    if match:
                        self.results['test_results'].append(match.groupdict())

parse = GtkTestParser(appendall={'units':'seconds', 'result':'pass'})
inst = abrek.testdef.AbrekTestInstaller(deps=["gtkperf"])
run = abrek.testdef.AbrekTestRunner(RUNSTEPS)

testobj = abrek.testdef.AbrekTest(testname="gtkperf", installer=inst,
                                  runner=run, parser=parse)

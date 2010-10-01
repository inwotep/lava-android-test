import abrek.testdef

RUNSTEPS = ["glmemperf"]
PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+) fps"

inst = abrek.testdef.AbrekTestInstaller(deps=["glmemperf"])
run = abrek.testdef.AbrekTestRunner(RUNSTEPS)
parse = abrek.testdef.AbrekTestParser(PATTERN,
                                      appendall={'units':'fps',
                                                 'result':'pass'})

testobj = abrek.testdef.AbrekTest(testname="glmemperf", installer=inst,
                                  runner=run, parser=parse)

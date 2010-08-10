import abrek.testdef

URL="http://www.cs.virginia.edu/stream/FTP/Code/stream.c"
MD5="b6cd43b848e0d8b0824703369392f3c5"
INSTALLSTEPS = ['cc stream.c -O2 -fopenmp -o stream']
RUNSTEPS = ['./stream']
PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+\.\d+)"

streaminst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, url=URL, md5=MD5)
streamrun = abrek.testdef.AbrekTestRunner(RUNSTEPS)
streamparser = abrek.testdef.AbrekTestParser(PATTERN,
               appendall={'units':'MB/s', 'result':'pass'})
testobj = abrek.testdef.AbrekTest(testname="stream", installer=streaminst,
                                  runner=streamrun, parser=streamparser)

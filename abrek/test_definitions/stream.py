import abrek.testdef

URL="http://www.cs.virginia.edu/stream/FTP/Code/stream.c"
MD5="b6cd43b848e0d8b0824703369392f3c5"
INSTALLSTEPS = ['cc stream.c -O2 -fopenmp -o stream']
RUNSTEPS = ['./stream']

streaminst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, url=URL, md5=MD5)
streamrun = abrek.testdef.AbrekTestRunner(RUNSTEPS)
testobj = abrek.testdef.AbrekTest(testname="stream", installer=streaminst,
                                  runner=streamrun)

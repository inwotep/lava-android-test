import abrek.testdef

URL="http://www.cs.virginia.edu/stream/FTP/Code/stream.c"
MD5="b6cd43b848e0d8b0824703369392f3c5"
STEPS = ['cc stream.c -O2 -fopenmp -o stream']

streaminst = abrek.testdef.AbrekTestInstaller(STEPS, url=URL, md5=MD5)
testobj = abrek.testdef.AbrekTest(testname="stream", installer=streaminst)

import abrek.testdef

URL="http://www.cs.virginia.edu/stream/FTP/Code/stream.c"
MD5="b6cd43b848e0d8b0824703369392f3c5"
INSTALLSTEPS = ['cc stream.c -O2 -fopenmp -o stream']
RUNSTEPS = ['./stream']
PATTERN = "^(?P<testid>\w+):\W+(?P<result>\d+\.\d+)"

class StreamTestParser(abrek.testdef.AbrekTestParser):
    def parse(self):
        super(StreamTestParser, self).parse()
        self.appendtoall({'units':'MB/s'})

streaminst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, url=URL, md5=MD5)
streamrun = abrek.testdef.AbrekTestRunner(RUNSTEPS)
streamparser = abrek.testdef.AbrekTestParser(PATTERN,
                             appendall={'units':'MB/s'})
testobj = abrek.testdef.AbrekTest(testname="stream", installer=streaminst,
                                  runner=streamrun, parser=streamparser)

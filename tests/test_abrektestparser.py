import os
import shutil
import tempfile
import unittest

from abrek.testdef import AbrekTestParser

class testAbrekTestParser(unittest.TestCase):
    def setUp(self):
        self.origdir = os.path.abspath(os.curdir)
        self.tmpdir = tempfile.mkdtemp()
        self.filename = os.path.abspath(__file__)
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.origdir)
        shutil.rmtree(self.tmpdir)

    def makeparser(self, *args, **kwargs):
        return AbrekTestParser(*args, **kwargs)

    def writeoutputlog(self, str):
        with open("testoutput.log", "a") as fd:
            fd.write(str)

    def test_parse(self):
        pattern = "^(?P<testid>\w+):\W+(?P<result>\w+)"
        self.writeoutputlog("test001: pass")
        parser = self.makeparser(pattern)
        parser.parse()
        self.assertTrue(parser.results["testlist"][0]["testid"] == "test001" and
                        parser.results["testlist"][0]["result"] == "pass")

    def test_fixupdict(self):
        pattern = "^(?P<testid>\w+):\W+(?P<result>\w+)"
        fixup = {"pass":"PASS"}
        self.writeoutputlog("test001: pass")
        parser = self.makeparser(pattern, fixupdict=fixup)
        parser.parse()
        self.assertEquals("PASS", parser.results["testlist"][0]["result"])

    def test_appendall(self):
        pattern = "^(?P<testid>\w+):\W+(?P<result>\w+)"
        append = {"units":"foo/s"}
        self.writeoutputlog("test001: pass")
        parser = self.makeparser(pattern, appendall=append)
        parser.parse()
        self.assertEqual("foo/s", parser.results["testlist"][0]["units"])


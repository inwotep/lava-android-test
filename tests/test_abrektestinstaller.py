import hashlib
import os
import shutil
import tempfile
import unittest

from abrek.testdef import AbrekTestInstaller

class testAbrekTestInstaller(unittest.TestCase):
    def setUp(self):
        self.origdir = os.path.abspath(os.curdir)
        self.tmpdir = tempfile.mkdtemp()
        self.filename = os.path.abspath(__file__)
        os.chdir(self.tmpdir)
        print self.tmpdir

    def tearDown(self):
        os.chdir(self.origdir)
        shutil.rmtree(self.tmpdir)

    def makeinstaller(self,**kwargs):
        return AbrekTestInstaller(**kwargs)

    def test_bad_md5(self):
        url = "file://%s" % self.filename
        installer = self.makeinstaller(url = url, md5 = 'foo')
        self.assertRaises(RuntimeError, installer._download)

    def test_good_md5(self):
        url = "file://%s" % self.filename
        md5 = hashlib.md5(file(self.filename).read()).hexdigest()
        installer = self.makeinstaller(url = url, md5 = md5)
        location = installer._download()
        self.assertTrue(os.path.exists(location))

    def test_runsteps(self):
        steps = ["echo test > foo"]
        installer = self.makeinstaller(steps = steps)
        installer._runsteps()
        self.assertTrue(os.path.exists("./foo"))
        #self.assertTrue(os.path.exists(self.tmpdir+"/foo"))

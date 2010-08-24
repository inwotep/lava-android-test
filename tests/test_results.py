import os
import sys
import tempfile
import unittest
import StringIO

import abrek.results
from abrek.config import set_config
from abrek.utils import read_file, write_file

class FakeOutputTests(unittest.TestCase):
        def setUp(self):
            self.origstdout = sys.stdout
            sys.stdout = self.fakestdout = StringIO.StringIO()

        def tearDown(self):
            sys.stdout = self.origstdout

class ResultsTests(FakeOutputTests):
    def setUp(self):
        super(ResultsTests, self).setUp()
        class fakeconfig:
            def __init__(self, basedir):
                self.configdir = os.path.join(basedir, "config")
                self.installdir = os.path.join(basedir, "install")
                self.resultsdir = os.path.join(basedir, "results")
        self.tmpdir = tempfile.mkdtemp()
        self.config = fakeconfig(self.tmpdir)
        set_config(self.config)

    def test_results_list(self):
        result_name = "test_results_list000"
        os.makedirs(os.path.join(self.config.resultsdir, result_name))
        cmd = abrek.results.subcmd_results_list()
        cmd.run()
        self.assertTrue(result_name in self.fakestdout.getvalue())

    def test_results_show(self):
        result_name = "test_results_show000"
        result_output = "test result output"
        result_dir = os.path.join(self.config.resultsdir, result_name)
        os.makedirs(result_dir)
        outputfile = os.path.join(result_dir, 'testoutput.log')
        write_file(result_output, outputfile)
        cmd = abrek.results.subcmd_results_show()
        cmd.main(argv=[result_name])
        self.assertEqual(result_output, self.fakestdout.getvalue().strip())

    def test_results_remove(self):
        result_name = "test_results_remove000"
        result_dir = os.path.join(self.config.resultsdir, result_name)
        os.makedirs(result_dir)
        cmd = abrek.results.subcmd_results_remove()
        cmd.main(argv=[result_name, '-f'])
        self.assertFalse(os.path.exists(result_dir))

    def test_results_rename(self):
        result_src = "test_results_old"
        result_dest = "test_results_new"
        result_srcdir = os.path.join(self.config.resultsdir, result_src)
        result_destdir = os.path.join(self.config.resultsdir, result_dest)
        os.makedirs(result_srcdir)
        cmd = abrek.results.subcmd_results_rename()
        cmd.main(argv=[result_src, result_dest])
        self.assertFalse(os.path.exists(result_srcdir))
        self.assertTrue(os.path.exists(result_destdir))

    def test_results_rename_badsrc(self):
        errmsg = "Result directory not found"
        result_src = "test_results_old"
        result_dest = "test_results_new"
        cmd = abrek.results.subcmd_results_rename()
        self.assertRaises(SystemExit, cmd.main, argv=[result_src, result_dest])
        self.assertEqual(errmsg, self.fakestdout.getvalue().strip())

    def test_results_rename_baddest(self):
        errmsg = "Destination result name already exists"
        result_src = "test_results_old"
        result_dest = "test_results_new"
        result_srcdir = os.path.join(self.config.resultsdir, result_src)
        result_destdir = os.path.join(self.config.resultsdir, result_dest)
        os.makedirs(result_srcdir)
        os.makedirs(result_destdir)
        cmd = abrek.results.subcmd_results_rename()
        self.assertRaises(SystemExit, cmd.main, argv=[result_src, result_dest])
        self.assertEqual(errmsg, self.fakestdout.getvalue().strip())

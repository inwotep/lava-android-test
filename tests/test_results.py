# Copyright (c) 2010 Linaro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

import abrek.results
from abrek.utils import write_file
from imposters import ConfigImposter, OutputImposter
from fixtures import TestCaseWithFixtures


class ResultsTests(TestCaseWithFixtures):
    def setUp(self):
        super(ResultsTests, self).setUp()
        self.config = self.add_fixture(ConfigImposter())
        self.out = self.add_fixture(OutputImposter())

    def test_results_list(self):
        result_name = "test_results_list000"
        os.makedirs(os.path.join(self.config.resultsdir, result_name))
        cmd = abrek.results.subcmd_results_list()
        cmd.run()
        self.assertTrue(result_name in self.out.getvalue())

    def test_results_list_nodir(self):
        errmsg = "No results found"
        cmd = abrek.results.subcmd_results_list()
        cmd.run()
        self.assertTrue(errmsg in self.out.getvalue())

    def test_results_show(self):
        result_name = "test_results_show000"
        result_output = "test result output"
        result_dir = os.path.join(self.config.resultsdir, result_name)
        os.makedirs(result_dir)
        outputfile = os.path.join(result_dir, 'testoutput.log')
        write_file(result_output, outputfile)
        cmd = abrek.results.subcmd_results_show()
        cmd.main(argv=[result_name])
        self.assertEqual(result_output, self.out.getvalue().strip())

    def test_results_show_noarg(self):
        errmsg = "please specify the name of the result dir"
        cmd = abrek.results.subcmd_results_show()
        self.assertRaises(SystemExit, cmd.main, argv=[])
        self.assertEqual(errmsg, self.out.getvalue().strip())

    def test_results_show_nodir(self):
        testname = "foo"
        errmsg = "No result found for '%s'" % testname
        cmd = abrek.results.subcmd_results_show()
        self.assertRaises(SystemExit, cmd.main, argv=[testname])
        self.assertEqual(errmsg, self.out.getvalue().strip())

    def test_results_remove(self):
        result_name = "test_results_remove000"
        result_dir = os.path.join(self.config.resultsdir, result_name)
        os.makedirs(result_dir)
        cmd = abrek.results.subcmd_results_remove()
        cmd.main(argv=[result_name, '-f'])
        self.assertFalse(os.path.exists(result_dir))

    def test_results_remove_noarg(self):
        errmsg = "please specify the name of the result dir"
        cmd = abrek.results.subcmd_results_remove()
        self.assertRaises(SystemExit, cmd.main, argv=[])
        self.assertEqual(errmsg, self.out.getvalue().strip())

    def test_results_remove_nodir(self):
        testname = "foo"
        errmsg = "No result found for '%s'" % testname
        cmd = abrek.results.subcmd_results_remove()
        self.assertRaises(SystemExit, cmd.main, argv=[testname])
        self.assertEqual(errmsg, self.out.getvalue().strip())

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
        self.assertEqual(errmsg, self.out.getvalue().strip())

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
        self.assertEqual(errmsg, self.out.getvalue().strip())

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
import shutil
import sys
from optparse import make_option

from abrek.command import AbrekCmd, AbrekCmdWithSubcommands
from abrek.config import get_config
from abrek.utils import read_file


class cmd_results(AbrekCmdWithSubcommands):
    """
    Operate on results of previous test runs stored locally
    """

    class cmd_list(AbrekCmd):
        """
        List results of previous runs
        """
        def run(self):
            config = get_config()
            print "Saved results:"
            try:
                for dir in os.listdir(config.resultsdir):
                    print dir
            except OSError:
                print "No results found"


    class cmd_show(AbrekCmd):
        """
        Display the output from a previous test run
        """
        arglist = ['*result']
        def run(self):
            if len(self.args) != 1:
                print "please specify the name of the result dir"
                sys.exit(1)
            config = get_config()
            resultsdir = os.path.join(config.resultsdir, self.args[0])
            testoutput = os.path.join(resultsdir, "testoutput.log")
            if not os.path.exists(testoutput):
                print "No result found for '%s'" % self.args[0]
                sys.exit(1)
            print(read_file(testoutput))


    class cmd_remove(AbrekCmd):
        """
        Remove the results of a previous test run
        """
        arglist = ['*result']
        options = [make_option('-f', '--force', action='store_true',
                               dest='force')]
        def run(self):
            if len(self.args) != 1:
                print "please specify the name of the result dir"
                sys.exit(1)
            config = get_config()
            resultsdir = os.path.join(config.resultsdir, self.args[0])
            if not os.path.exists(resultsdir):
                print "No result found for '%s'" % self.args[0]
                sys.exit(1)
            if not self.opts.force:
                print "Delete result '%s' for good? [Y/N]" % self.args[0],
                response = raw_input()
                if response[0].upper() != 'Y':
                    sys.exit(0)
            shutil.rmtree(resultsdir)


    class cmd_rename(AbrekCmd):
        """
        Rename the results from a previous test run
        """
        arglist = ['*source', '*destination']

        def run(self):
            if len(self.args) != 2:
                print "please specify the name of the result, and the new name"
                sys.exit(1)
            config = get_config()
            srcdir = os.path.join(config.resultsdir, self.args[0])
            destdir = os.path.join(config.resultsdir, self.args[1])
            if not os.path.exists(srcdir):
                print "Result directory not found"
                sys.exit(1)
            if os.path.exists(destdir):
                print "Destination result name already exists"
                sys.exit(1)
            shutil.move(srcdir, destdir)



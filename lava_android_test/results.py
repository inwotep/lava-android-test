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
import sys
from optparse import make_option

from lava_android_test.command import AndroidTestCmd, AndroidTestCmdWithSubcommands
from lava_android_test.config import get_config
from lava_android_test.adb import ADB

class cmd_results(AndroidTestCmdWithSubcommands):
    """
        Operate on results of previous test runs stored on android device
    """
    class cmd_list(AndroidTestCmd):
        """
        List results of previous runs
        """
        options = [make_option('-s', '--serial', 
                               help='Specify the serial number when multiple devices connected')]

        def run(self):
            config = get_config()
            print "Saved results:"
            try:
                adb=ADB(self.opts.serial)
                (ret_code, output)=adb.listdir(config.resultsdir_android)
                if ret_code != 0:
                    raise OSError()
                for dir in output:
                    print dir.strip()
            except OSError:
                print "No results found"


    class cmd_show(AndroidTestCmd):
        """
        Display the output from a previous test run
        """
        arglist = ['*result']
        options = [make_option('-s', '--serial', 
                               help='Specify the serial number when multiple devices connected')]

        def run(self):
            if len(self.args) != 1:
                print "please specify the name of the result dir"
                sys.exit(1)
            config = get_config()
            resultsdir = os.path.join(config.resultsdir_android, self.args[0])
            testoutput = os.path.join(resultsdir, "testoutput.log")
            adb = ADB(self.opts.serial)
            if not adb.exists(testoutput):
                print "No result found for '%s'" % self.args[0]
                sys.exit(1)
            try:
                output = adb.read_file(testoutput)
                if output is not None:
                    for line in output.readlines():
                        print line.strip()
            except IOError:
                pass


    class cmd_remove(AndroidTestCmd):
        """
        Remove the results of a previous test run
        """
        arglist = ['*result']
        options = [make_option('-f', '--force', action='store_true',
                               dest='force'),
                   make_option('-s', '--serial', 
                               help='Specify the serial number when multiple devices connected')]
        def run(self):
            if len(self.args) != 1:
                print "please specify the name of the result dir"
                sys.exit(1)
            config = get_config()
            resultsdir = os.path.join(config.resultsdir_android, self.args[0])
            adb = ADB(self.opts.serial)
            if not adb.exists(resultsdir):
                print "No result found for '%s'" % self.args[0]
                sys.exit(1)
            if not self.opts.force:
                print "Delete result '%s' for good? [Y/N]" % self.args[0],
                response = raw_input()
                if response[0].upper() != 'Y':
                    sys.exit(0)
            adb.rmtree(resultsdir)


    class cmd_rename(AndroidTestCmd):
        """
        Rename the results from a previous test run
        """
        arglist = ['*source', '*destination']
        options = [make_option('-s', '--serial', 
                               help='Specify the serial number when multiple devices connected')]

        def run(self):
            if len(self.args) != 2:
                print "please specify the name of the result, and the new name"
                sys.exit(1)
            config = get_config()
            srcdir = os.path.join(config.resultsdir_android, self.args[0])
            destdir = os.path.join(config.resultsdir_android, self.args[1])
            adb = ADB(self.opts.serial)
            if not adb.exists(srcdir):
                print "Result directory not found"
                sys.exit(1)
            if adb.exists(destdir):
                print "Destination result name already exists"
                sys.exit(1)
            adb.move(srcdir, destdir)



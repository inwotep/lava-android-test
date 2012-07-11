# Copyright (c) 2012 Linaro

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
import traceback

from pkgutil import walk_packages

from lava_android_test import testdef
from lava_android_test import test_definitions
from lava_android_test.test_definitions import commands, instruments
from lava_android_test.adb import ADB
from lava_android_test.config import get_config
from lava_android_test.utils import find_files


class UnfoundTest(Exception):
    """
    Raise this for unfound test errors
    """


class TestProvider(object):

    test_prefix = ''

    def list_test(self):
        """
        Return the list of this type
        """
        raise NotImplementedError()

    def import_mod(self, importpath):
        try:
            mod = __import__(importpath)
        except ImportError:
            raise UnfoundTest('The module(%s) is not found!' % importpath)
        for i in importpath.split('.')[1:]:
            mod = getattr(mod, i)
        return mod

    def list_mod(self, pkg_path):
        test_list = []
        for importer, mod, ispkg in walk_packages(pkg_path):
            test_list.append(mod)
        return test_list

    def gen_testobj(self, testname=None, installer=None, runner=None,
                    parser=None, adb=ADB()):

        if installer is None:
            installer = testdef.AndroidTestInstaller()
        if runner is None:
            runner = testdef.AndroidTestRunner()
        if parser is None:
            parser = testdef.AndroidTestParser()

        testobj = testdef.AndroidTest(testname=testname,
                            installer=installer, runner=runner, parser=parser)

        testobj.parser.results = {'test_results': []}
        testobj.setadb(adb)
        return testobj

    def get_test_provider_list(self):
        providers_hash = {}
#        module = imp.load_source("module", os.path.realpath(__file__))
        module = self.import_mod('lava_android_test.provider')
        for name, cls in module.__dict__.iteritems():
            if name.endswith('TestProvider') \
                and name != 'TestProvider':
                providers_hash[name] = cls
        names = providers_hash.keys()
        names.sort()
        providers_list = []
        common_test_provider = None
        for name in names:
            if name != 'CommonTestProvider':
                providers_list.append(providers_hash.get(name))
            else:
                common_test_provider = providers_hash.get(name)
        if common_test_provider is not None:
            providers_list.append(common_test_provider)
        return providers_list

    def load_test(self, test_name=None, serial=''):
        providers = self.get_test_provider_list()
        err_msg = ''
        for provider in providers:
            try:
                testobj = provider().load_test(test_name=test_name,
                                                serial=serial)
                if testobj is not None:
                    return testobj
            except:
                err_msg = err_msg + traceback.format_exc()
        raise UnfoundTest('The test(%s) is not found! + Exception:\n%s' % (
                                                       test_name, err_msg))


class CommonTestProvider(TestProvider):

    def list_test(self):
        return self.list_mod(test_definitions.__path__)

    def load_test(self, test_name=None, serial=None):
        importpath = "lava_android_test.test_definitions.%s" % test_name
        mod = self.import_mod(importpath)

        base = mod.testobj
        base.parser.results = {'test_results': []}
        base.setadb(ADB(serial))
        return base


class CommandTestProvider(TestProvider):

    test_prefix = 'command'

    def list_test(self):
        test_list = self.list_mod(commands.__path__)
        ret_list = []
        for test_id in test_list:
            ret_list.append('%s-%s' % (self.test_prefix, test_id))
        return ret_list

    def load_test(self, test_name=None, serial=None):
        if not test_name.startswith('%s-' % self.test_prefix):
            raise UnfoundTest('The test(%s) is not found!' % test_name)
        mod_name = test_name.replace('%s-' % self.test_prefix, '', 1)
        importpath = "lava_android_test.test_definitions.%ss.%s" % (
                            self.test_prefix, mod_name)
        mod = self.import_mod(importpath)
        if not mod.RUN_ADB_SHELL_STEPS:
            raise UnfoundTest(("RUN_ADB_SHELL_STEPS not"
                            " defined in the test(%s).") % test_name)
        if not mod.PATTERN:
            raise UnfoundTest(("PATTERN not"
                            " defined in the test(%s).") % test_name)
        testobj = self.gen_testobj(
                    testname=test_name,
                    runner=testdef.AndroidTestRunner(
                        adbshell_steps=mod.RUN_ADB_SHELL_STEPS),
                    parser=testdef.AndroidTestParser(pattern=mod.PATTERN),
                    adb=ADB(serial))
        return testobj


class InstrumentTestProvider(TestProvider):

    test_prefix = 'instrument'

    def list_test(self):
        test_list = self.list_mod(instruments.__path__)
        ret_list = []
        for test_id in test_list:
            ret_list.append('%s-%s' % (self.test_prefix, test_id))
        return ret_list

    def load_test(self, test_name=None, serial=None):
        if not test_name.startswith('%s-' % self.test_prefix):
            raise UnfoundTest('The test(%s) is not found!' % test_name)
        mod_name = test_name.replace('%s-' % self.test_prefix, '', 1)
        importpath = "lava_android_test.test_definitions.%ss.%s" % (
                            self.test_prefix, mod_name)
        mod = self.import_mod(importpath)
        if not mod.RUN_ADB_SHELL_STEPS:
            raise UnfoundTest(("RUN_ADB_SHELL_STEPS not"
                            " defined in the test(%s).") % test_name)

        testobj = self.gen_testobj(
                    testname=test_name,
                    runner=testdef.AndroidTestRunner(
                            adbshell_steps=mod.RUN_ADB_SHELL_STEPS),
                    parser=testdef.AndroidInstrumentTestParser(),
                    adb=ADB(serial))
        return testobj


class ShellTestProvider(TestProvider):

    test_prefix = 'shell'
    config = get_config()
    dotext = '.sh'

    def list_test(self):
        dotext = '.sh'
        mod = self.import_mod("lava_android_test.test_definitions.shells")
        sh_files = find_files(mod.curdir, dotext)
        test_list = []
        for f in sh_files:
            ##Assume that the file name only has one '.sh'
            f_name_no_dotext = os.path.basename(f).replace(dotext, '')
            test_list.append('%s-%s' % (self.test_prefix, f_name_no_dotext))
        return test_list

    def load_test(self, test_name=None, serial=None):
        if not test_name.startswith('%s-' % self.test_prefix):
            raise UnfoundTest('The test(%s) is not found!' % test_name)
        f_name_no_dotext = test_name.replace('%s-' % self.test_prefix, '', 1)

        mod = self.import_mod("lava_android_test.test_definitions.%ss" %
                            self.test_prefix)
        f_name = '%s%s' % (f_name_no_dotext, self.dotext)
        sh_file = '%s/%s' % (mod.curdir, f_name)

        test_sh_android_path = os.path.join(self.config.installdir_android,
                                test_name, f_name)

        INSTALL_STEPS_ADB_PRE = [
                     'push %s %s ' % (sh_file, test_sh_android_path),
                     'shell chmod 777 %s' % test_sh_android_path]

        ADB_SHELL_STEPS = ['%s $(OPTIONS)' % test_sh_android_path]
        PATTERN = ("^\s*(?P<test_case_id>\S+)="
                   "(?P<result>(pass|fail|ok|ng|true|false|skip|done))\s*$")

        testobj = self.gen_testobj(
                    testname=test_name,
                    installer=testdef.AndroidTestInstaller(
                                steps_adb_pre=INSTALL_STEPS_ADB_PRE),
                    runner=testdef.AndroidTestRunner(
                                    adbshell_steps=ADB_SHELL_STEPS),
                    parser=testdef.AndroidTestParser(PATTERN),
                    adb=ADB(serial))
        return testobj


class HostShellTestProvider(TestProvider):

    test_prefix = 'hostshell'
    config = get_config()
    dotext = '.sh'

    def list_test(self):
        dotext = '.sh'
        mod = self.import_mod("lava_android_test.test_definitions.hostshells")
        sh_files = find_files(mod.curdir, dotext)
        test_list = []
        for f in sh_files:
            ##Assume that the file name only has one '.sh'
            f_name_no_dotext = os.path.basename(f).replace(dotext, '')
            test_list.append('%s-%s' % (self.test_prefix, f_name_no_dotext))
        return test_list

    def load_test(self, test_name=None, serial=None):
        if not test_name.startswith('%s-' % self.test_prefix):
            raise UnfoundTest('The test(%s) is not found!' % test_name)
        f_name_no_prefix = test_name.replace('%s-' % self.test_prefix, '', 1)

        mod = self.import_mod("lava_android_test.test_definitions.%ss" %
                            self.test_prefix)
        f_name = '%s%s' % (f_name_no_prefix, self.dotext)
        test_sh_path = '%s/%s' % (mod.curdir, f_name)

        HOST_SHELL_STEPS = ['bash %s -s $(SERIAL) $(OPTIONS)' % test_sh_path]
        PATTERN = ("^\s*(?P<test_case_id>\S+)="
                   "(?P<result>(pass|fail|ok|ng|true|false|skip|done))\s*$")

        testobj = self.gen_testobj(
                    testname=test_name,
                    installer=testdef.AndroidTestInstaller(),
                    runner=testdef.AndroidTestRunner(
                                    steps_host_pre=HOST_SHELL_STEPS),
                    parser=testdef.AndroidTestParser(PATTERN),
                    adb=ADB(serial))
        return testobj


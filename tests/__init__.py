# Copyright (c) 2010, 2011 Linaro
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

import unittest

def test_suite():
    module_names = [
                   # 'tests.test_lavaandroidtest_commands',
                   # 'tests.test_lavaandroidtest_test',
                   # 'tests.test_lavaandroidtest_testinstaller',
                   # 'tests.test_lavaandroidtest_testparser',
                   # 'tests.test_lavaandroidtest_testrunner',
                    'tests.test_swprofile',
                    'tests.test_hwprofile']
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(module_names)
    return suite

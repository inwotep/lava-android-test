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


class BuiltInProvider(object):
    """
    Test provider that provides tests shipped in the Abrek source tree
    """

    _builtin_tests = [
        'monkey',
        '0xbench'
    ]

    def __init__(self, config):
        pass

    @property
    def description(self):
        return "Tests built directly into LAVA Test:"

    def __iter__(self):
        return iter(self._builtin_tests)

    def __getitem__(self, test_id):
        if test_id not in self._builtin_tests:
            raise KeyError(test_id)
        module = __import__("lava_android_test.test_definitions.%s" % test_id,
                            fromlist=[''])
        return module.testobj

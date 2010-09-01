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

import unittest

class TestCaseWithFixtures(unittest.TestCase):
    """TestCase extended to allow adding fixtures

    Fixtures added should contain at least a setUp() method, and
    optionally a tearDown method as well
    """

    def add_fixture(self, fixture):
        if not hasattr(self, "_fixtures"):
            self._fixtures = []
        fixture.setUp()
        if hasattr(self, "tearDown"):
            self._fixtures.append(fixture)
        return fixture

    def cleanup(self):
        for fixture in self._fixtures:
            fixture.tearDown()
        self._fixtures = []

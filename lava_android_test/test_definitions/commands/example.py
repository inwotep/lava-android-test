# Copyright (c) 2012 Linaro

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
#
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

"""
Example for how to add tests that only need to run an android command
and specify the output pattern to parse the command ouput to get result.

**URL:** None

**Default options:** None
"""
RUN_ADB_SHELL_STEPS = ['tjunittest']
PATTERN = ("^\s*(?P<test_case_id>.+)\s+\.\.\.\s+(?P<result>\w+)\."
           "\s+(?P<measurement>[\d\.]+)\s+(?P<units>\w+)\s*$")

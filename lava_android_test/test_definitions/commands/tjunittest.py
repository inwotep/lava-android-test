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
Tests the various code paths in the TurboJPEG C Wrapper

**URL:** https://git.linaro.org/gitweb?p=people/tomgall/libjpeg-turbo/libjpeg-turbo.git;a=blob_plain;f=tjunittest.c

**Default options:** None
"""
ADB_SHELL_STEPS = ['tjunittest']
PATTERN = ("^\s*(?P<test_case_id>.+)\s+\.\.\.\s+(?P<result>\w+)\."
           "\s+(?P<measurement>[\d\.]+)\s+(?P<units>\w+)\s*$")

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
Runs the linaro kernel unit tests including:
    ashmem/ashmem_expanded/alarmdev/logger/binder/sync

**URL:**  https://linaro-private.git.linaro.org/gitweb?p=android/linaro-android-kernel-test.git;a=summary

**Default Options:** None
"""

RUN_ADB_SHELL_STEPS = ['linaro-android-kernel-tests.sh']
PATTERN = "\s*\[(?P<test_case_id>\w+)\]:\s\w+\s(?P<result>\w+)"

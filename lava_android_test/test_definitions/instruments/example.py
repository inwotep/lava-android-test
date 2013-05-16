# copyright (C) 2012 Linaro Limited
#
# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
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
Example for how to add instrument tests into lava-android-test.
You can try this test with the android emulator which has this test integrated.

**URL:** http://android.git.linaro.org/gitweb?p=platform/development.git;a=blob;f=tools/emulator/test-apps/ConnectivityTest/src/com/android/emulator/connectivity/test/ConnectivityTest.java;h=9931eb849928926d99be98cd1de62baefe610310;hb=HEAD

**Default options:** None
"""

cmd = ("am instrument -r -w "
       "com.android.emulator.connectivity.test/"
       "android.test.InstrumentationTestRunner")
RUN_ADB_SHELL_STEPS = [cmd]

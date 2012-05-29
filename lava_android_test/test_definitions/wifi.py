# copyright (C) 2011-2012 Linaro Limited
#
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
import lava_android_test.testdef

test_name = 'wifi'

cmd = ("am instrument -r -w "
       "com.android.wifi.tests/android.wifi.WifiTestRunner")
RUN_ADB_SHELL_STEPS = [cmd]

inst = lava_android_test.testdef.AndroidTestInstaller()
run = lava_android_test.testdef.AndroidTestRunner(
                                adbshell_steps=RUN_ADB_SHELL_STEPS)
parser = lava_android_test.testdef.AndroidInstrumentTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                                installer=inst,
                                                runner=run,
                                                parser=parser)

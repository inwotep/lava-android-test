# Copyright (c) 2011 Linaro
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

import lava_android_test.swprofile
from tests.tests_util import fake_adb, clear_fake

package_list_info = '''android:4.0.1.2.3.4.5.6.7.8.9-3 (#14)
com.android.musicvis:4.0.1.2.3.4.5.6.7.8.9-3 (#14)
com.android.videoeditor:1.1 (#11)
com.android.vpndialogs:4.0.1.2.3.4.5.6.7.8.9-3 (#14)
com.android.wallpaper:4.0.1.2.3.4.5.6.7.8.9-3 (#14)
com.android.wallpaper.livepicker:4.0.1.2.3.4.5.6.7.8.9-3 (#14)
com.svox.pico:1.0 (#1)'''

getprop_info = '''[dalvik.vm.heapsize]: [24m]
[dalvik.vm.stack-trace-file]: [/data/anr/traces.txt]
[dev.bootcomplete]: [1]
[gsm.current.phone-type]: [1]
[ro.build.date]: [Wed Oct 12 12:35:47 PDT 2011]
[ro.build.description]: [sdk-eng 4.0.1 ICS_MR0 202595 test-keys]
[ro.build.display.id]: [sdk-eng 4.0.1 ICS_MR0 202595 test-keys]
[ro.build.host]: [android-test-37.mtv.corp.google.com]
[ro.build.id]: [ICS_MR0]
[ro.build.product]: [generic]
[ro.build.tags]: [test-keys]
[ro.build.type]: [eng]
[ro.build.version.sdk]: [14]'''

class SwprofileTests(unittest.TestCase):
    maxDiff = None

    def test_getimage_name_from_properties(self):
        fake_adb(output_str=getprop_info)
        image_name = lava_android_test.swprofile.get_image_name_from_properties()
        clear_fake()
        self.assertEqual('sdk-eng 4.0.1 ICS_MR0 202595 test-keys', image_name)

    def test_get_properties(self):
        fake_adb(output_str=getprop_info)
        result = lava_android_test.swprofile.get_properties()
        clear_fake()
        properties = {'dalvik.vm.heapsize': '24m',
                    'dalvik.vm.stack-trace-file': '/data/anr/traces.txt',
                    'dev.bootcomplete': '1',
                    'gsm.current.phone-type': '1',
                    'ro.build.date': 'Wed Oct 12 12:35:47 PDT 2011',
                    'ro.build.description': 'sdk-eng 4.0.1 ICS_MR0 202595 test-keys',
                    'ro.build.display.id': 'sdk-eng 4.0.1 ICS_MR0 202595 test-keys',
                    'ro.build.host': 'android-test-37.mtv.corp.google.com',
                    'ro.build.id': 'ICS_MR0',
                    'ro.build.product': 'generic',
                    'ro.build.tags': 'test-keys',
                    'ro.build.type': 'eng',
                    'ro.build.version.sdk': '14'}
        self.assertEqual(properties, result)

    def test_get_package_info(self):
        fake_adb(output_str=package_list_info)
        result = lava_android_test.swprofile.get_package_info()
        clear_fake()
        packages = {'android':'4.0.1.2.3.4.5.6.7.8.9-3 (#14)',
                    'com.android.musicvis':'4.0.1.2.3.4.5.6.7.8.9-3 (#14)',
                    'com.android.videoeditor':'1.1 (#11)',
                    'com.android.vpndialogs':'4.0.1.2.3.4.5.6.7.8.9-3 (#14)',
                    'com.android.wallpaper':'4.0.1.2.3.4.5.6.7.8.9-3 (#14)',
                    'com.android.wallpaper.livepicker':'4.0.1.2.3.4.5.6.7.8.9-3 (#14)',
                    'com.svox.pico':'1.0 (#1)'}
        result_hash = {}
        for package in result:
            result_hash[package.get('name')] = package.get('version')

        self.assertEqual(packages, result_hash)


#!/usr/bin/env python
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

import lava_android_test.hwprofile
from tests.tests_util import fake_adb, clear_fake

from tests.imposters import OutputImposter
from tests.fixtures import TestCaseWithFixtures

FAKE_BOARDNAME_FILE = "XXXXXXX"
FAKE_BOARDVENDOR_FILE = "YYYYYYY"
FAKE_BOARDVERSION_FILE = "ZZZZZZZ"

panda_cpu_info = '''Processor    : ARMv7 Processor rev 2 (v7l)
processor    : 0
BogoMIPS    : 1576.53

processor    : 1
BogoMIPS    : 1539.77

Features    : swp half thumb fastmult vfp edsp thumbee neon vfpv3 tls
CPU implementer    : 0x41
CPU architecture: 7
CPU variant    : 0x1
CPU part    : 0xc09
CPU revision    : 2

Hardware    : OMAP4 Panda board
Revision    : 0020
Serial        : 0000000000000000
'''

panda_mem_info = '''MemTotal:         921832 kB
MemFree:          545032 kB
Buffers:             488 kB
Cached:           183964 kB
SwapCached:            0 kB
Active:           212628 kB
Inactive:         125480 kB
Active(anon):     153680 kB
Inactive(anon):    60744 kB
Active(file):      58948 kB
Inactive(file):    64736 kB
Unevictable:           0 kB
Mlocked:               0 kB
HighTotal:        211968 kB
HighFree:            408 kB
LowTotal:         709864 kB
LowFree:          544624 kB
SwapTotal:             0 kB
SwapFree:              0 kB
Dirty:                 0 kB
Writeback:             0 kB
AnonPages:        153640 kB
Mapped:           105236 kB
Shmem:             60768 kB
Slab:              10728 kB
SReclaimable:       4760 kB
SUnreclaim:         5968 kB
KernelStack:        3272 kB
PageTables:         5528 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:      460916 kB
Committed_AS:    4237400 kB
VmallocTotal:     122880 kB
VmallocUsed:       75536 kB
VmallocChunk:      36868 kB
'''


class HwprofileTests(unittest.TestCase):
    maxDiff = None

    def test_get_cpu_devs(self):
        fake_adb(output_str=panda_cpu_info)
        devs = lava_android_test.hwprofile.get_cpu_devs()
        clear_fake()
        cpuinfo = {
            'attributes': {
                'processor': '1',
                'cpu_features':
                    'swp half thumb fastmult vfp edsp thumbee neon vfpv3 tls',
                'cpu_variant': 1,
                'cpu_architecture': 7,
                'BogoMIPS': '1539.77',
                'Hardware': 'OMAP4 Panda board',
                'cpu_implementer': 65,
                'cpu_part': 3081,
                'cpu_revision': 2,
                'Serial': '0000000000000000',
                'Revision': '0020'},
            'description': 'Processor #1',
            'device_type': 'device.cpu'}
        self.assertEqual(cpuinfo, devs[1])
        cpuinfo = {
            'attributes': {
                'processor': '0',
                'cpu_model_name': 'ARMv7 Processor rev 2 (v7l)',
                'BogoMIPS': '1576.53'},
            'description': 'Processor #0',
            'device_type': 'device.cpu'}
        self.assertEqual(cpuinfo, devs[0])

    def test_get_board_devs(self):
        fake_adb(output_str=panda_cpu_info)
        devs = lava_android_test.hwprofile.get_board_devs()
        clear_fake()
        boardinfo = {
            'description': 'OMAP4 Panda board',
            'device_type': 'device.board'}
        self.assertEqual(boardinfo, devs[0])

    def test_get_mem_devs(self):
        fake_adb(output_str=panda_mem_info)
        devs = lava_android_test.hwprofile.get_mem_devs()
        clear_fake()

        meminfo = {
            'attributes': {
                'kind': 'RAM',
                'capacity': '943955968'},
            'description': '900MiB of RAM',
            'device_type': 'device.mem'}
        self.assertEqual(meminfo, devs[0])


class MissingFiles(TestCaseWithFixtures):
    """
    These are tests for situations where certain files used for gathering
    hardware profile information may be missing
    """
    def setUp(self):
        super(MissingFiles, self).setUp()
        clear_fake()
        self.out = self.add_fixture(OutputImposter())

    def test_bad_cpuinfo(self):
        errmsg = 'WARNING: Could not read cpu information\n'
        fake_adb(output_str='', ret_code=255)
        devs = lava_android_test.hwprofile.get_cpu_devs()
        clear_fake()
        self.assertEqual([], devs)
        self.assertEqual(errmsg, self.out.getvalue())

    def test_bad_boardinfo(self):
        errmsg = 'WARNING: Could not read board information\n'
        fake_adb(output_str='', ret_code=255)
        devs = lava_android_test.hwprofile.get_board_devs()
        clear_fake()
        self.assertEqual([], devs)
        self.assertEqual(errmsg, self.out.getvalue())

    def test_bad_meminfo(self):
        errmsg = 'WARNING: Could not read memory information\n'
        fake_adb(output_str='', ret_code=255)
        devs = lava_android_test.hwprofile.get_mem_devs()
        clear_fake()
        self.assertEqual([], devs)
        self.assertEqual(errmsg, self.out.getvalue())


if __name__ == '__main__':
    unittest.main()

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

import os
import unittest

import abrek.hwprofile
from abrek.utils import fake_file, clear_fakes, fake_machine, clear_fake_machine
from imposters import OutputImposter
from fixtures import TestCaseWithFixtures


class AptCache:
    def __init__(self, packages=[]):
        self.packages = packages

ARM_CPUINFO_FILE = """Processor       : ARMv7 Processor rev 3 (v7l)
BogoMIPS        : 483.16
Features        : swp half thumb fastmult vfp edsp neon vfpv3*
CPU implementer : 0x41
CPU architecture: 7
CPU variant     : 0x1
CPU part        : 0xc08
CPU revision    : 3

Hardware        : OMAP3 Beagle Board
Revision        : 0020
Serial          : 0000000000000000"""

FAKE_BOARDNAME_FILE = "XXXXXXX"
FAKE_BOARDVENDOR_FILE = "YYYYYYY"
FAKE_BOARDVERSION_FILE = "ZZZZZZZ"

FAKE_MEMINFO_FILE = """MemTotal:         238220 kB
MemFree:           45992 kB
Buffers:            4564 kB
Cached:            73220 kB
SwapCached:        15536 kB
Active:            48460 kB
Inactive:         122624 kB
Active(anon):      18788 kB
Inactive(anon):    75888 kB
Active(file):      29672 kB
Inactive(file):    46736 kB
Unevictable:           0 kB
Mlocked:               0 kB
SwapTotal:        524284 kB
SwapFree:         458436 kB
Dirty:                 0 kB
Writeback:             0 kB
AnonPages:         81076 kB
Mapped:             9556 kB
Shmem:              1376 kB
Slab:              11072 kB
SReclaimable:       4408 kB
SUnreclaim:         6664 kB
KernelStack:        1656 kB
PageTables:         2748 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:      643392 kB
Committed_AS:     398812 kB
VmallocTotal:     647168 kB
VmallocUsed:        1936 kB
VmallocChunk:     643316 kB"""

class HwprofileTests(unittest.TestCase):
    def test_get_cpu_devs_arm(self):
        fake_file('/proc/cpuinfo', ARM_CPUINFO_FILE)
        fake_machine('arm')
        devs = abrek.hwprofile.get_cpu_devs()
        clear_fake_machine()
        cpuinfo = {
            'attributes': {
                'cpu_model_name': 'ARMv7 Processor rev 3 (v7l)',
                'cpu_features': 'swp half thumb fastmult vfp edsp neon vfpv3*',
                'cpu_variant': 1,
                'cpu_architecture': 7,
                'BogoMIPS': '483.16',
                'Hardware': 'OMAP3 Beagle Board',
                'cpu_implementer': 65,
                'cpu_part': 3080,
                'cpu_revision': 3,
                'Serial': '0000000000000000',
                'Revision': '0020'},
            'description': 'Processor #0',
            'device_type': 'device.cpu'}
        self.assertEqual(cpuinfo, devs[0])

    def test_get_board_devs_x86(self):
        fake_machine('x86_64')
        fake_file('/sys/class/dmi/id/board_name', FAKE_BOARDNAME_FILE)
        fake_file('/sys/class/dmi/id/board_vendor',
            FAKE_BOARDVENDOR_FILE)
        fake_file('/sys/class/dmi/id/board_version',
            FAKE_BOARDVERSION_FILE)
        boardinfo = {
            'attributes': {
                'version': 'ZZZZZZZ',
                'vendor': 'YYYYYYY'},
            'description': 'XXXXXXX',
            'device_type': 'device.board'}
        devs = abrek.hwprofile.get_board_devs()
        clear_fake_machine()
        self.assertEqual(boardinfo, devs[0])

    def test_get_board_devs_arm(self):
        fake_machine('arm')
        fake_file('/proc/cpuinfo', ARM_CPUINFO_FILE)
        boardinfo = {
            'description': 'OMAP3 Beagle Board',
            'device_type': 'device.board'}
        devs = abrek.hwprofile.get_board_devs()
        clear_fake_machine()
        self.assertEqual(boardinfo, devs[0])

    def test_get_mem_devs(self):
        fake_file('/proc/meminfo', FAKE_MEMINFO_FILE)
        devs = abrek.hwprofile.get_mem_devs()
        meminfo = {
            'attributes': {
                'kind': 'RAM',
                'capacity': '243937280'},
            'description': '232MiB of RAM',
            'device_type': 'device.mem'}
        self.assertEqual(meminfo, devs[0])

    def test_get_usb_devs(self):
        devs = abrek.hwprofile.get_usb_devs()
        self.assertEqual('device.usb', devs[0]['device_type'])


class MissingFiles(TestCaseWithFixtures):
    """
    These are tests for situations where certain files used for gathering
    hardware profile information may be missing
    """
    def setUp(self):
        super(MissingFiles, self).setUp()
        clear_fakes()
        self.out = self.add_fixture(OutputImposter())

    def test_bad_cpuinfo(self):
        errmsg = "WARNING: Could not read cpu information\n"
        fake_file('/proc/cpuinfo', newpath='/foo/bar')
        devs = abrek.hwprofile.get_cpu_devs()
        self.assertEqual([], devs)
        self.assertEqual(errmsg, self.out.getvalue())

    def test_bad_boardinfo(self):
        fake_machine('x86_64')
        errmsg = "WARNING: Could not read board information\n"
        fake_file('/sys/class/dmi/id/board_name', newpath='/foo/bar')
        fake_file('/proc/cpuinfo', newpath='/foo/bar')
        devs = abrek.hwprofile.get_board_devs()
        clear_fake_machine()
        self.assertEqual([], devs)
        self.assertEqual(errmsg, self.out.getvalue())

    def test_bad_meminfo(self):
        errmsg = "WARNING: Could not read memory information\n"
        fake_file('/proc/meminfo', newpath='/foo/bar')
        devs = abrek.hwprofile.get_mem_devs()
        self.assertEqual([], devs)
        self.assertEqual(errmsg, self.out.getvalue())


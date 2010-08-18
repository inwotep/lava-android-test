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

import abrek.hwprofile
from abrek.utils import fake_file

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
    def test_get_cpu_devs(self):
        fake_file('/proc/cpuinfo', ARM_CPUINFO_FILE)
        devs = abrek.hwprofile.get_cpu_devs()
        processor = "ARMv7 Processor rev 3 (v7l)"
        self.assertEqual(processor, devs[0]['desc']['Processor'])

    def test_get_board_devs(self):
        fake_file('/sys/class/dmi/id/board_name', FAKE_BOARDNAME_FILE)
        devs = abrek.hwprofile.get_board_devs()
        self.assertEqual(FAKE_BOARDNAME_FILE, devs[0]['attributes'])

    def test_get_mem_devs(self):
        fake_file('/proc/meminfo', FAKE_MEMINFO_FILE)
        devs = abrek.hwprofile.get_mem_devs()
        self.assertEqual(243937280, devs[0]['desc']['capacity'])

    def test_get_usb_devs(self):
        devs = abrek.hwprofile.get_usb_devs()
        self.assertEqual('device.usb', devs[0]['device_type'])

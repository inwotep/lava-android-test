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

import re
import sys
from lava_android_test.adb import ADB

ARM_KEYMAP = {
    'Processor': 'cpu_model_name',
    'Features': 'cpu_features',
    'CPU implementer': 'cpu_implementer',
    'CPU architecture': 'cpu_architecture',
    'CPU variant': 'cpu_variant',
    'CPU part': 'cpu_part',
    'CPU revision': 'cpu_revision',
}

ARM_VALMAP = {
    'CPU implementer': lambda value: int(value, 16),
    'CPU architecture': int,
    'CPU variant': lambda value: int(value, 16),
    'CPU part': lambda value: int(value, 16),
    'CPU revision': int,
}


def _translate_cpuinfo(keymap, valmap, key, value):
    """
    Translate a key and value using keymap and valmap passed in
    """
    newkey = keymap.get(key, key)
    newval = valmap.get(key, lambda x: x)(value)
    return newkey, newval

def get_cpu_devs(adb=ADB()):
    """
    Return a list of CPU devices
    """

    pattern = re.compile('^(?P<key>.+?)\s*:\s*(?P<value>.*)$')
    cpunum = 0
    devices = []
    cpudevs = []
    cpudevs.append({})

    # TODO maybe there is other types
    keymap, valmap = ARM_KEYMAP, ARM_VALMAP

    try:
        (retcode, cpuinfo) = adb.get_shellcmdoutput("cat /proc/cpuinfo")
        if retcode != 0 or cpuinfo is None :
            raise IOError("Faile to get content of file(%s)" % "/proc/cpuinfo")
        for line in cpuinfo:
            match = pattern.match(line)
            if match:
                key, value = match.groups()
                key = key.strip()
                value = value.strip()
                try:
                    key, value = _translate_cpuinfo(keymap, valmap, key, value)
                except ValueError:
                    pass
                if cpudevs[cpunum].get(key):
                    cpunum += 1
                    cpudevs.append({})
                cpudevs[cpunum][key] = value
        for c in range(len(cpudevs)):
            device = {}
            device['device_type'] = 'device.cpu'
            device['description'] = 'Processor #{0}'.format(c)
            device['attributes'] = cpudevs[c]
            devices.append(device)
    except IOError:
        print >> sys.stderr, "WARNING: Could not read cpu information"
    return devices

def get_board_devs(adb=ADB()):
    """
    Return a list of board devices
    """
    devices = []
    attributes = {}
    device = {}

    try:
        (retcode, cpuinfo) = adb.get_shellcmdoutput("cat /proc/cpuinfo")
        if retcode != 0 or cpuinfo is None :
            raise IOError("Faile to get content of file(%s)" % "/proc/cpuinfo")
        pattern = re.compile("^Hardware\s*:\s*(?P<description>.+)$", re.M)
        found = False
        for line in cpuinfo:
            match = pattern.search(line)
            if match :
                found = True
                device['description'] = match.group('description').strip()
        if not found:
            return devices
    except IOError:
        print >> sys.stderr, "WARNING: Could not read board information"
        return devices
    if attributes:
        device['attributes'] = attributes
    device['device_type'] = 'device.board'
    devices.append(device)
    return devices

def get_mem_devs(adb=ADB()):
    """ Return a list of memory devices

    This returns up to two items, one for physical RAM and another for swap
    """
    devices = []

    pattern = re.compile('^(?P<key>.+?)\s*:\s*(?P<value>.+) kB$', re.M)

    try:
        (retcode, meminfo) = adb.get_shellcmdoutput("cat /proc/meminfo")
        if retcode != 0 or meminfo is None:
            raise IOError("Faile to get content of file(%s)" % "/proc/meminfo")
        for line in meminfo:
            match = pattern.search(line)
            if not match:
                continue
            key, value = match.groups()
            key = key.strip()
            value = value.strip()
            if key not in ('MemTotal', 'SwapTotal'):
                continue
            capacity = int(value) << 10 #Kernel reports in 2^10 units
            if capacity == 0:
                continue
            if key == 'MemTotal':
                kind = 'RAM'
            else:
                kind = 'swap'
            description = "{capacity}MiB of {kind}".format(
                capacity=capacity >> 20, kind=kind)
            device = {}
            device['description'] = description
            device['attributes'] = {'capacity': str(capacity), 'kind': kind}
            device['device_type'] = "device.mem"
            devices.append(device)
    except IOError:
        print >> sys.stderr, "WARNING: Could not read memory information"
    return devices

def get_hardware_context(adb=ADB()):
    """
    Return a dict with all of the hardware profile information gathered
    """
    hardware_context = {}
    devices = []
    devices.extend(get_cpu_devs(adb))
    devices.extend(get_board_devs(adb))
    devices.extend(get_mem_devs(adb))
    hardware_context['devices'] = devices
    return hardware_context

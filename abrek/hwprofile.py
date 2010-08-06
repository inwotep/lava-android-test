import commands
import os
import re
from utils import read_file

INTEL_KEYMAP = {
    'vendor_id': 'cpu_vendor_name',
    'cpu family': 'cpu_family',
    'model': 'cpu_model',
    'model name': 'cpu_model_name',
    'stepping': 'cpu_stepping',
    'cpu MHz': 'cpu_mhz',
    'flags': 'cpu_features',
}

INTEL_VALMAP = {
    'cpu family': int,
    'model': int,
    'stepping': int,
    'cpu MHz': float,
    'flags': lambda value: list(sorted(value.split())),
}

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
    'Features': lambda value: list(sorted(value.split()))
}


def _translate_cpuinfo(keymap, valmap, key, value):
    """
    Translate a key and value using keymap and valmap passed in
    """
    newkey = keymap.get(key, key)
    newval = valmap.get(key, lambda x: x)(value)
    return newkey, newval

def get_cpu_devs():
    """
    Return a list of CPU devices
    """
    pattern = re.compile('^(?P<key>.+?)\s*:\s*(?P<value>.*)$')
    cpunum = 0
    devices = []
    cpudevs = []
    cpudevs.append({})
    machine = os.uname()[-1]
    if machine in ('i686', 'x86_64'):
        keymap, valmap = INTEL_KEYMAP, INTEL_VALMAP
    elif machine.startswith('arm'):
        keymap, valmap = ARM_KEYMAP, ARM_VALMAP

    cpuinfo = read_file("/proc/cpuinfo")
    for line in cpuinfo.splitlines():
        match = pattern.match(line)
        if match:
            key, value = match.groups()
            key, value = _translate_cpuinfo(keymap, valmap,
                         key, value)
            if cpudevs[cpunum].get(key):
                cpunum += 1
                cpudevs.append({})
            cpudevs[cpunum][key] = value
    for c in range(len(cpudevs)):
        device = {}
        device['device_type'] = 'device.cpu'
        device['attributes'] = 'Processor #{0}'.format(c)
        device['desc'] = cpudevs[c]
        devices.append(device)
    return devices


def get_board_devs():
    """
    Return a list of board devices
    """
    devices = []
    desc = {}
    device = {}
    machine = os.uname()[-1]
    if machine in ('i686', 'x86_64'):
        name = read_file('/sys/class/dmi/id/board_name') or None
        vendor = read_file('/sys/class/dmi/id/board_vendor') or None
        version = read_file('/sys/class/dmi/id/board_version') or None
        if name:
            device['attributes'] = name.strip()
        if vendor:
            desc['vendor'] = vendor.strip()
        if version:
            desc['version'] = version.strip()
    elif machine.startswith('arm'):
        cpuinfo = read_file("/proc/cpuinfo")
        if cpuinfo is None:
            return devices
        pattern = re.compile("^Hardware\s*:\s*(?P<hardware>.+)$", re.M)
        match = pattern.search(cpuinfo)
        if match is None:
            return devices
        desc['hardware'] = match.group('hardware')
    else:
        return devices
    device['desc'] = desc
    device['device_type'] = 'device.board'
    devices.append(device)
    return devices

def get_mem_devs():
    """ Return a list of memory devices

    This returns up to two items, one for physical RAM and another for swap
    """
    pattern = re.compile('^(?P<key>.+?)\s*:\s*(?P<value>.+) kB$', re.M)

    devices = []
    meminfo = read_file("/proc/meminfo")
    for match in pattern.finditer(meminfo):
        key, value = match.groups()
        if key not in ('MemTotal', 'SwapTotal'):
            continue
        capacity = int(value) << 10 #Kernel reports in 2^10 units
        if capacity == 0:
            continue
        if key == 'MemTotal':
            kind = 'RAM'
        else:
            kind = 'swap'
        name = "{capacity}MiB of {kind}".format(
               capacity=capacity >> 20, kind=kind)
        device = {}
        device['attributes'] = name
        device['desc'] = {'capacity': capacity, 'kind': kind}
        device['device_type'] = "device.mem"
        devices.append(device)
    return devices

def get_usb_devs():
    """
    Return a list of usb devices
    """
    pattern = re.compile(
              "^Bus \d{3} Device \d{3}: ID (?P<vendor_id>[0-9a-f]{4}):"
              "(?P<product_id>[0-9a-f]{4}) (?P<name>.*)$")
    devices = []
    for line in commands.getoutput('lsusb').splitlines():
        match = pattern.match(line)
        if match:
            vendor_id, product_id, name = match.groups()
            desc = {}
            device = {}
            desc['vendor_id'] = int(vendor_id, 16)
            desc['product_id'] = int(product_id, 16)
            device['desc'] = desc
            device['attributes'] = name
            device['device_type'] = 'device.usb'
            devices.append(device)
    return devices

def get_hw_context():
    """
    Return a dict with all of the hardware profile information gathered
    """
    hw_context = {}
    devices = []
    devices.extend(get_cpu_devs())
    devices.extend(get_board_devs())
    devices.extend(get_mem_devs())
    devices.extend(get_usb_devs())
    hw_context['devices'] = devices
    return hw_context


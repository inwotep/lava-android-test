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
import re
import sys
from datetime import datetime
from lava_android_test.adb import ADB
from lava_android_test.config import get_config

def get_properties(adb=ADB()):
    if adb is None:
        return {}

    properties = {}
    try:
        propinfo = adb.get_shellcmdoutput("getprop")[1]
        if propinfo is None:
            return properties
        pattern = re.compile('^\[(?P<key>[^\]]+?)]\s*:\s*\[(?P<value>[^\]]+)\]\s*$', re.M)
        for line in propinfo:
            match = pattern.search(line)
            if match :
                key, value = match.groups()
                properties[key] = value
    except IOError:
        print >> sys.stderr, "WARNING: Could not read board information"
        return properties
    return properties

def get_image_name_from_properties(adb=ADB()):
    props = get_properties(adb)
    return props.get('ro.build.display.id')

def get_source_info(adb=ADB()):

    TIMEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
    source = []
    example = {'project_name':'',
               'branch_vcs':'git',
               'branch_url':'',
               'branch_revision':'',
               'commit_timestamp':datetime.utcnow().strftime(TIMEFORMAT)}
    source.append(example)
    return source

def get_package_info(adb=ADB()):

    packages_info = []
    pkginfo = adb.get_shellcmdoutput('/system/bin/pm list packages -v')[1]
    if pkginfo is None:
        return packages_info
    pattern = re.compile('^\s*package:\s*(?P<package_name>[^:]+?)\s*:\s*(?P<version>[^\s].+)\s*$', re.M)
    for line in pkginfo:
        match = pattern.search(line)
        if match :
            package_name, version = match.groups()
            package = {'name':package_name.strip(),
                'version':version.strip()}
            packages_info.append(package)
    return packages_info

def get_software_context(adb=ADB()):
    """ Return dict used for storing software_context information

    test_id - Unique identifier for this test
    time_check - whether or not a check was performed to see if
            the time on the system was synced with a time server
    apt_cache - if not provided, this will be read from the system
    lsb_information - if not provided, this will be read from the system
    """
    if adb is None:
        return {}

    software_context = {'image': {'name':get_image_name_from_properties(adb)},
                        'sources':get_source_info(adb),
                        'packages':get_package_info(adb)
                        }
    return software_context

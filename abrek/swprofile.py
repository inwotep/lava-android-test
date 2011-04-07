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

import apt
import lsb_release
from utils import read_file

def get_packages(apt_cache=None):
    """ Get information about the packages installed

    apt_cache - if not provided, this will be read from the system
    """
    if apt_cache == None:
        apt_cache = apt.Cache()
    packages = []
    for apt_pkg in apt_cache:
        if hasattr(apt_pkg, 'is_installed'):
            is_installed = apt_pkg.is_installed
        else:
            is_installed = apt_pkg.isInstalled # old style API
        if is_installed:
            pkg = {"name":apt_pkg.name, "version":apt_pkg.installed.version}
            packages.append(pkg)
    return packages

def get_software_context(apt_cache=None, lsb_information=None):
    """ Return dict used for storing software_context information

    test_id - Unique identifier for this test
    time_check - whether or not a check was performed to see if
            the time on the system was synced with a time server
    apt_cache - if not provided, this will be read from the system
    lsb_information - if not provided, this will be read from the system
    """
    software_context = {}
    software_context['image'] = get_image(lsb_information)
    software_context['packages'] = get_packages(apt_cache)
    return software_context

def get_image(lsb_information=None):
    """ Get information about the image we are running

    If /etc/buildstamp exists, get the image id from that.  Otherwise
    just use the lsb-release description for a rough idea.
    """
    try:
        buildstamp = read_file("/etc/buildstamp")
        name = buildstamp.splitlines()[1]
    except IOError:
        if lsb_information == None:
            lsb_information = lsb_release.get_lsb_information()
        name = lsb_information['DESCRIPTION']
    return {"name":name}

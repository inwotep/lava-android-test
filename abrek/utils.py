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

import shutil
import os
import urllib2
import urlparse

_fake_files = None

def geturl(url, path=""):
    urlpath = urlparse.urlsplit(url).path
    filename = os.path.basename(urlpath)
    if path:
        filename = os.path.join(path,filename)
    fd = open(filename, "w")
    try:
        response = urllib2.urlopen(url)
        fd = open(filename, 'wb')
        shutil.copyfileobj(response,fd,0x10000)
        fd.close()
        response.close()
    except:
        raise RuntimeError("Could not retrieve %s" % url)
    return filename

def write_file(data, path):
    with open(path, "w") as fd:
        fd.write(data)

def read_file(path):
    global _fake_files
    if _fake_files is not None:
        if path in _fake_files:
            return _fake_files[path]
    with open(path) as fd:
        data = fd.read()
    return data

def fake_file(path, data):
    """
    Set up a fake file to be read with read_file() in testing
    """
    global _fake_files
    if _fake_files is None:
        _fake_files = {}
    _fake_files[path] = data

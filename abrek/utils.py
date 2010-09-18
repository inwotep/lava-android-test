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
_fake_paths = None

def geturl(url, path=""):
    urlpath = urlparse.urlsplit(url).path
    filename = os.path.basename(urlpath)
    if path:
        filename = os.path.join(path,filename)
    fd = open(filename, "w")
    try:
        response = urllib2.urlopen(urllib2.quote(url, safe=":/"))
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
    global _fake_paths
    if _fake_files is not None:
        if path in _fake_files:
            return _fake_files[path]
    if _fake_paths is not None:
        if path in _fake_paths:
            path = _fake_paths[path]
    with open(path) as fd:
        data = fd.read()
    return data

def fake_file(path, data=None, newpath=None):
    """
    Set up a fake file to be read with read_file() in testing
    If data is specified, the string passed as data will be returned instead
    if newpath is specified, the file attempted to be read will be replaced
    by newfile
    """
    global _fake_files
    global _fake_paths
    if data is not None:
        if _fake_files is None:
            _fake_files = {}
        _fake_files[path] = data
    if newpath is not None:
        if _fake_paths is None:
            _fake_paths = {}
        _fake_paths[path] = newpath

def clear_fakes():
    global _fake_files
    global _fake_paths
    _fake_files = {}
    _fake_paths = {}

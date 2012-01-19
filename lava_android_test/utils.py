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
import os
import shutil
import subprocess
import sys
import urllib2
import urlparse

_fake_files = None
_fake_paths = None
_fake_machine = None


class Tee(file):
    """ A file-like object that optionally mimics tee functionality.

    By default, output will go to both stdout and the file specified.
    Optionally, quiet=True can be used to mute the output to stdout.
    """
    def __init__(self, *args, **kwargs):
        try:
            self.quiet = kwargs.pop('quiet')
        except KeyError:
            self.quiet = False
        super(Tee, self).__init__(*args, **kwargs)

    def write(self, data):
        super(Tee, self).write(data)
        if self.quiet is False:
            sys.stdout.write(data)


def geturl(url, path=""):
    urlpath = urlparse.urlsplit(url).path
    filename = os.path.basename(urlpath)
    if path:
        filename = os.path.join(path, filename)
    fd = open(filename, "w")
    try:
        response = urllib2.urlopen(urllib2.quote(url, safe=":/"))
        fd = open(filename, 'wb')
        shutil.copyfileobj(response, fd, 0x10000)
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


def fake_machine(type):
    """
    Set up a fake machine type for testing
    """
    global _fake_machine
    _fake_machine = type


def clear_fakes():
    global _fake_files
    global _fake_paths
    _fake_files = {}
    _fake_paths = {}


def clear_fake_machine():
    global _fake_machine
    _fake_machine = None


def run_and_log(cmd, fd, quiet=False):
    """
    Run a command and log the output to fd
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, shell=True)
    while proc.returncode == None:
        proc.poll()
        data = proc.stdout.readline()
        fd.write(data)
        if quiet is False:
            sys.stdout.write(data)
    return proc.returncode


def get_machine_type():
    """
    Return the machine type
    """
    global _fake_machine
    if _fake_machine is None:
        return os.uname()[-1]
    return _fake_machine

def get_local_name(url):
    url = url.strip()
    url = re.sub('[\/]+$', '', url)
    rest = urllib2.splittype(url)[1]
    host, rest = urllib2.splithost(rest)
    if rest is None or  rest == '':
        return host
    return os.path.basename(rest)

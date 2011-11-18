#!/usr/bin/python

# Copyright (c) 2011 Linaro

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
#
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
import sys
import re
import os
from commands import getstatusoutput

curdir = os.path.realpath(os.path.dirname(__file__))
source = '%s/ZeroxBench_Preference.xml' % curdir
target = '/data/data/org.zeroxlab.zeroxbenchmark/shared_prefs/ZeroxBench_Preference.xml'

if len(sys.argv) == 1:
    adbcmd = 'adb'
else:
    adbcmd = 'adb -s %s' % (sys.argv[1])

target_dir = '/data/data'
lscmd = '%s shell ls -l  %s' % (adbcmd, target_dir)
rc, output = getstatusoutput(lscmd)
if rc != 0:
    print 'Failed to get group and owner of directory(%s) : %s' % (target_dir, output)
    sys.exit(1)
group = None
owner = None
##drwxr-x--x app_76   app_76            2011-10-21 14:40 org.zeroxlab.zeroxbenchmark
pattern = re.compile('^d\S+\s+(?P<group>\S+?)\s+(?P<owner>\S+?)\s+\S+\s+\S+\s+org\.zeroxlab\.zeroxbenchmark\s*$')
for line in output.splitlines():
    match = pattern.match(line)
    if match:
        group, owner = match.groups()
        break
if (group is None) or (owner is None):
    print 'Failed to get group and owner of directory(%s): %s' % (target_dir, output)
    sys.exit(1)

target_dir = '/data/data/org.zeroxlab.zeroxbenchmark/shared_prefs'
mkdircmd = '%s shell mkdir %s' % (adbcmd, target_dir)
rc, output = getstatusoutput(mkdircmd)
if rc != 0:
    print 'Failed to create directory(%s): %s' % (source, target, output)
    sys.exit(1)

chowncmd = '%s shell chown %s.%s %s' % (adbcmd, owner, group, target_dir)
rc, output = getstatusoutput(chowncmd)
if rc != 0:
    print 'Failed to change group(%s) and owner(%s) of file(%s): %s' % (group, owner, target_dir, output)
    sys.exit(1)

chmodcmd = '%s shell chmod 771 %s' % (adbcmd, target_dir)
rc, output = getstatusoutput(chmodcmd)
if rc != 0:
    print 'Failed to change chmod to 771 for file(%s): %s' % (target_dir, output)
    sys.exit(1)

pushcmd = '%s push %s %s' % (adbcmd, source, target)
rc, output = getstatusoutput(pushcmd)
if rc != 0:
    print 'Failed to push file(%s) to file(%s): %s' % (source, target, output)
    sys.exit(1)

chowncmd = '%s shell chown %s.%s %s' % (adbcmd, owner, group, target)
rc, output = getstatusoutput(chowncmd)
if rc != 0:
    print 'Failed to change group(%s) and owner(%s) of file(%s): %s' % (group, owner, target, output)
    sys.exit(1)

chmodcmd = '%s shell chmod 660 %s' % (adbcmd, target)
rc, output = getstatusoutput(chmodcmd)
if rc != 0:
    print 'Failed to change chmod to 771 for file(%s): %s' % (target, output)
    sys.exit(1)

target_dir = '/data/data/org.zeroxlab.zeroxbenchmark/files'
mkdircmd = '%s shell mkdir %s' % (adbcmd, target_dir)
rc, output = getstatusoutput(mkdircmd)
if rc != 0:
    print 'Failed to create directory(%s): %s' % (target_dir, output)
    sys.exit(1)

chowncmd = '%s shell chown %s.%s %s' % (adbcmd, owner, group, target_dir)
rc, output = getstatusoutput(chowncmd)
if rc != 0:
    print 'Failed to change group(%s) and owner(%s) of file(%s): %s' % (group, owner, target_dir, output)
    sys.exit(1)

chmodcmd = '%s shell chmod 771 %s' % (adbcmd, target_dir)
rc, output = getstatusoutput(chmodcmd)
if rc != 0:
    print 'Failed to change chmod to 771 for file(%s): %s' % (target_dir, output)
    sys.exit(1)


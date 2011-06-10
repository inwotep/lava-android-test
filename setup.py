#!/usr/bin/env python

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

from abrek import __version__ as version
import sys

try:
    from DistUtilsExtra.auto import setup
except ImportError:
    print >> sys.stderr, 'To build lava-test you need', \
                         'https://launchpad.net/python-distutils-extra'
    sys.exit(1)

setup(
name='lava-test',
version=version,
author='Paul Larson',
author_email='paul.larson@linaro.org',
url='https://launchpad.net/lava-test',
description='Lava test execution framework',
long_description=open("README").read() + "\n",
)

#!/usr/bin/env python

# Copyright (c) 2010, 2011 Linaro
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

from setuptools import setup, find_packages
from abrek import __version__ as version


setup(
    name='lava-test',
    version=version,
    author='Linaro Validation Team',
    author_email='linaro-dev@lists.linaro.org',
    url='https://launchpad.net/lava-test',
    description='Lava test execution framework',
    long_description=open("README").read(),
    packages=find_packages(exclude=['tests']),
    license="GNU GPLv3",
    test_suite='tests.test_suite',
    scripts = ['bin/lava-test'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Testing",
    ],
    zip_safe=False,
    include_package_data=True)


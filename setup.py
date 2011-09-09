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


setup(
    name='lava-android-test',
    version=":versiontools:lava_android_test:",
    author='Linaro Validation Team',
    author_email='linaro-dev@lists.linaro.org',
    url='https://launchpad.net/lava-android-test',
    description='LAVA android test execution framework',
    long_description=open("README").read(),
    packages=find_packages(exclude=['tests']),
    license="GNU GPLv3",
    test_suite='tests.test_suite',
    entry_points="""
    [console_scripts]
    lava-android-test=lava_android_test.main:main
    [lava_android_test.commands]
    version=lava_android_test.commands:version
    list-devices=lava_android_test.commands:list_devices
    list-tests=lava_android_test.commands:list_tests
    list-installed=lava_android_test.commands:list_installed
    list-results=lava_android_test.commands:list_results
    install=lava_android_test.commands:install
    uninstall=lava_android_test.commands:uninstall
    run=lava_android_test.commands:run
    parse=lava_android_test.commands:parse
    show=lava_android_test.commands:show
    rename=lava_android_test.commands:rename
    remove=lava_android_test.commands:remove
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Testing",
    ],
    install_requires=[
        'lava-tool >= 0.2',
        'versiontools >= 1.4',
        'linaro_dashboard_bundle',
    ],
    setup_requires=[
        'versiontools >= 1.4'
    ],
    zip_safe=False,
    include_package_data=True)

#!/bin/bash
# Copyright (C) 2012 Linaro Limited

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
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

#http://source.android.com/compatibility/downloads.html

cts_pkg="android-cts-4.0.3_r3-linux_x86-arm.zip"
media_pkg="android-cts-media-1.0.zip"
site_url="https://dl.google.com/dl/android/cts/"
test_str='--plan CTS'
#site_url="http://192.168.1.127/images/cts/"
#test_str='--package android.admin'
#test_str='--plan AppSecurity'

cts_pkg_url="${site_url}${cts_pkg}"
media_pkg_url="${site_url}${media_pkg}"

ADB_OPTION=""
SERIAL=""
if [ "x${1}" != "x" ]; then
    ADB_OPTION="-s ${1}"
    SERIAL="${1}"
fi
ADB_CMD="adb ${ADB_OPTION}"


function download_unzip(){
    if [ -z "$1" ] || [ -z "$2" ]; then
        return
    fi
    url="${1}"
    pkg="${2}"
    
    echo "wget -i ${url} -O ${pkg}"
    wget "${url}" -O ${pkg}
    if [ $? -ne 0 ]; then
        echo "Failed to get the package ${url}"
        exit 1
    fi
    echo "unzip ${pkg}"
    unzip ${pkg}
    if [ $? -ne 0 ]; then
        echo "Faild to unzip the package "
        exit 1
    fi
}

rm -fr android-cts.zip android-cts
download_unzip "${cts_pkg_url}" ${cts_pkg}
download_unzip "${media_pkg_url}" ${media_pkg}

echo "adb ${ADB_OPTION} shell mkdir /mnt/sdcard/test"
chmod +x copy_media.sh
echo "copy_media.sh all ${ADB_OPTION}"
/bin/bash ./copy_media.sh all ${ADB_OPTION}

echo "${ADB_CMD} install -r android-cts/repository/testcases/CtsDeviceAdmin.apk"
${ADB_CMD} install -r android-cts/repository/testcases/CtsDeviceAdmin.apk
if [ $? -ne 0 ]; then
    echo "Faild to install CtsDeviceAdmin.apk"
    exit 1
fi

if [ "x${1}" != "x" ]; then
    echo "./android-cts/tools/cts-tradefed run cts --serial ${SERIAL} ${test_str}|tee cts_output.log"
    ./android-cts/tools/cts-tradefed run cts --serial ${SERIAL} ${test_str}|tee cts_output.log
else
    echo "./android-cts/tools/cts-tradefed run cts ${test_str}|tee cts_output.log"
    ./android-cts/tools/cts-tradefed run cts ${test_str}|tee cts_output.log
fi

exit 0

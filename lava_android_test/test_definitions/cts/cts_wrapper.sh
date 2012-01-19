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

ADB_CMD="adb"
if [ "x${1}" != "x" ]; then
    ADB_CMD="${ADB_CMD} -s ${1}"
fi

cts_url_txt='https://wiki.linaro.org/TestDataLinkPage?action=AttachFile&do=get&target=android-cts-url.txt'
mix_zip_name='mix.zip'
android_cts_name='android-cts.zip'

rm -fr android-cts.zip android-cts

echo "wget -i ${cts_url_txt} -O ${mix_zip_name}"
wget -i "${cts_url_txt}" -O ${mix_zip_name}
if [ $? -ne 0 ]; then
    echo "Failed to get the android-cts packages"
    exit 1
fi
echo "tail --lines=+2 ${mix_zip_name}>${android_cts_name}"
tail --lines=+2 ${mix_zip_name}>${android_cts_name}
if [ $? -ne 0 ]; then
    echo "Failed to get the android-cts packages from downloaded packages"
    exit 1
fi

echo "unzip ${android_cts_name}"
unzip ${android_cts_name}
if [ $? -ne 0 ]; then
    echo "Faild to unzip the android-cts packages"
    exit 1
fi

echo "${ADB_CMD} install -r android-cts/repository/testcases/CtsDeviceAdmin.apk"
${ADB_CMD} install -r android-cts/repository/testcases/CtsDeviceAdmin.apk
if [ $? -ne 0 ]; then
    echo "Faild to install CtsDeviceAdmin.apk"
    exit 1
fi

RET_CODE=0
#test_str='--package android.admin'
test_str='--plan AppSecurity'
test_str='--plan CTS'
if [ "x${1}" != "x" ]; then
    echo "./android-cts/tools/cts-tradefed run cts --serial ${1} ${test_str}|tee cts_output.log"
    ./android-cts/tools/cts-tradefed run cts --serial ${1} ${test_str}|tee cts_output.log
    RET_CODE=$?
else
    echo "./android-cts/tools/cts-tradefed run cts ${test_str}|tee cts_output.log"
    ./android-cts/tools/cts-tradefed run cts ${test_str}|tee cts_output.log
    RET_CODE=$?
fi
rm -f tee cts_output.log
if [ ${RET_CODE} -ne 0 ]; then
    echo "Faild to run cts for test (${test_str})"
    exit 1
fi
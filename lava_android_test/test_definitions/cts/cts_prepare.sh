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

cts_pkg="android-cts-linux_x86-arm-latest.zip"
media_pkg="android-cts-media-latest.zip"
site_url="http://testdata.validation.linaro.org/cts/"
#site_url="http://192.168.1.127/images/cts/"
#export http_proxy=http://localhost:3128

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
    
    echo "wget --connect-timeout=30 -S --progress=dot -e dotbytes=2M ${url} -O ${pkg}"
    wget -c -t 20 --connect-timeout=30 -S --progress=dot -e dotbytes=2M "${url}" -O ${pkg}
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

function main(){
    rm -fr ${cts_pkg} ${media_pkg} android-cts
    download_unzip "${cts_pkg_url}" ${cts_pkg}

    #1. Your phone should be running a user build (Android 4.0 and later) from source.android.com
    #2. Please refer to this link on the Android developer site and set up your device accordingly.
    #3. Make sure that your device has been flashed with a user build (Android 4.0and later) before you run CTS.
    ####Step 1~3 is done by deployment
	
    #4. You need to ensure the Text To Speech files are installed on the device. 
    #   You can check via Settings > Speech synthesis > Install voice data 
    #   before running CTS tests. 
    #   (Note that this assumes you have Android Market installed on the device, 
    #   if not you will need to install the files manually via adb)
    ##TODO don't know how to do this yet
	
    #5. Make sure the device has a SD card plugged in and the card is empty. 
    #   Warning: CTS may modify/erase data on the SD card plugged in to the device.
    #6. Do a factory data reset on the device (Settings > SD Card & phone storage >Factory data reset). 
    #   Warning: This will erase all user data from the phone.
    #7. Make sure no lock pattern is set on the device (Settings > Security > Screen Lock should be 'None').
    #8. Make sure the "USB Debugging" development option is checked (Settings >Developer options > USB debugging).
    #9. Make sure Settings > Developer options > Stay Awake is checked
    #10. Make sure Settings > Developer options > Allow mock locations is checked
    ####Step 5~10 is done by deployment
	
    #11. Make sure device is connected to a functioning Wi-Fi network (Settings > WiFi)
    ${ADB_CMD} shell am start -a android.intent.action.MAIN -n com.android.settings/.Settings
    ${ADB_CMD} shell service call wifi 13 i32 1
    sleep 5
	
    #12. Make sure the device is at the home screen at the start of CTS (Press the home button).
    ${ADB_CMD} shell input keyevent 3
    sleep 3
	
    #13. While a device is running tests, it must not be used for any other tasks.
    #14. Do not press any keys on the device while CTS is running. 
    #    Pressing keys or touching the screen of a test device will interfere with the running tests and may lead to test failures.
    #####Steps 13~14 should be the ok because nobody will operation the test target.
	
    #15. Set up accessibility tests:
    echo "${ADB_CMD} install -r android-cts/repository/testcases/CtsDelegatingAccessibilityService.apk"
    ${ADB_CMD} install -r android-cts/repository/testcases/CtsDelegatingAccessibilityService.apk
    if [ $? -ne 0 ]; then
        echo "Faild to install CtsDelegatingAccessibilityService.apk"
        exit 1
    fi
    ##TODO On the device, enable Settings > Accessibility > DelegatingAccessibility Service
	
    #16. Set up device administration tests:
    echo "${ADB_CMD} install -r android-cts/repository/testcases/CtsDeviceAdmin.apk"
    ${ADB_CMD} install -r android-cts/repository/testcases/CtsDeviceAdmin.apk
    if [ $? -ne 0 ]; then
        echo "Faild to install CtsDeviceAdmin.apk"
        exit 1
    fi
    ##TODO On the device, enable Settings > Security > Device Administrators >android.deviceadmin.cts.CtsDeviceAdmin* settings
	
	exit 0
}

main "$@"

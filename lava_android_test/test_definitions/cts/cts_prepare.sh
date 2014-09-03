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
if [ -z "$cts_pkg" ]; then
cts_pkg="android-cts-4.4_r3-linux_x86-arm.zip"
fi
media_pkg="android-cts-media-1.0.zip"
#site_url="http://testdata.validation.linaro.org/cts/"
#site_url="http://192.168.1.127/images/cts/"
#export http_proxy=http://localhost:3128
site_url="file:///home/smertz/"

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
    
    echo "curl ${url} > ${pkg}"
    curl ${url} > ${pkg}
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
    ${ADB_CMD} push $2 /data/local/tmp/
    #12. Make sure Settings > Developer options > Stay Awake is checked
    #13. Make sure Settings > Developer options > Allow mock locations is checked
    ${ADB_CMD} shell uiautomator runtest ctshelper.jar -c com.linaro.ctshelper#DeveloperOptionsEnableHelper
    ${ADB_CMD} shell uiautomator runtest ctshelper.jar -c com.linaro.ctshelper#DeveloperOptionsHelper

    #9. Make sure no lock pattern is set on the device (Settings > Security > Screen Lock should be 'None').
    ${ADB_CMD} shell uiautomator runtest ctshelper.jar -c com.linaro.ctshelper#ScreenLockHelper

    rm -fr ${cts_pkg} ${media_pkg} android-cts
    download_unzip "${cts_pkg_url}" ${cts_pkg}
    download_unzip "${media_pkg_url}" ${media_pkg}

    #1. Your phone should be running a user build (Android 4.0 and later) from source.android.com
    #2. Please refer to this link on the Android developer site and set up your device accordingly.
    #3. Make sure that your device has been flashed with a user build (Android 4.0and later) before you run CTS.
    #4. Make sure the device has a SD card plugged in and the card is empty.
    #   Warning: CTS may modify/erase data on the SD card plugged in to the device.
    #5. Do a factory data reset on the device (Settings > SD Card & phone storage >Factory data reset).
    #   Warning: This will erase all user data from the phone.
    ####Step 1~5 is done by deployment


    #6. Make sure your device is set up with English (United States) as the language
    ${ADB_CMD} shell uiautomator runtest ctshelper.jar -c com.linaro.ctshelper#LanguageHelper

    #7. Ensure the device has the Location setting On.
    ${ADB_CMD} shell uiautomator runtest ctshelper.jar -c com.linaro.ctshelper#LocationHelper

    #8. Make sure the device is connected to a functioning Wi-Fi network (Settings>Wi-Fi) that supports IPv6
    ${ADB_CMD} shell uiautomator runtest ctshelper.jar -c com.linaro.ctshelper#WifiHelper
    #TODO This will just turn it on


    #10. Make sure the "USB Debugging" development option is checked (Settings >Developer options > USB debugging).
    #11. Connect the host machine that will be used to test the device, and "Allow USB debugging" for the computer's RSA key.
    ####Step 10~11 is done by deployment


    #14. Not applicable

    #15. Set up device administration tests:
    echo "${ADB_CMD} install -r android-cts/repository/testcases/CtsDeviceAdmin.apk"
    ${ADB_CMD} install -r android-cts/repository/testcases/CtsDeviceAdmin.apk
    if [ $? -ne 0 ]; then
        echo "Faild to install CtsDeviceAdmin.apk"
        exit 1
    fi

    ## On the device, enable Settings > Security > Device Administrators >android.deviceadmin.cts.CtsDeviceAdmin* settings
    ${ADB_CMD} shell uiautomator runtest ctshelper.jar -c com.linaro.ctshelper#SecurityHelper

	#16. Copy the media files to the device's external storage
	echo "bash copy_media.sh 1920x1080 ${ADB_OPTION}"
	bash copy_media.sh 1920x1080 ${ADB_OPTION}

    #17. Make sure the device is at the home screen at the start of CTS (Press the home button).
    ${ADB_CMD} shell input keyevent 3
    sleep 3

    #18. While a device is running tests, it must not be used for any other tasks.
    #19. Do not press any keys on the device while CTS is running.
    #    Pressing keys or touching the screen of a test device will interfere with the running tests and may lead to test failures.
    #####Steps 18~19 should be the ok because nobody will operation the test target.

    #20. Launch the browser and dismiss any startup/setup screen
    #TODO

	exit 0
}

main "$@"

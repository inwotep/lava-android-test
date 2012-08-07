#!/bin/bash
# Copyright (c) 2012 Linaro

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

function generate_wpa_conf(){
    conf=$1 && ssid=$2 passwd=$3
    if [ -z "${conf}" ];then
        return
    fi

    if [ -z "${ssid}" ]; then
        cat >wpa_supplicant.conf <<__EOF__
ctrl_interface=wlan0
update_config=1
device_type=0-00000000-0

__EOF__

    elif [ -z "${passwd}" ]; then
        cat >wpa_supplicant.conf <<__EOF__
ctrl_interface=wlan0
update_config=1
device_type=0-00000000-0

network={
	ssid="${ssid}"
	key_mgmt=NONE
	priority=2
}

__EOF__

    else
        cat >wpa_supplicant.conf <<__EOF__
ctrl_interface=wlan0
update_config=1
device_type=0-00000000-0

network={
	ssid="${ssid}"
	psk="${passwd}"
	key_mgmt=WPA-PSK
	priority=2
}

__EOF__

    fi
}

function enable_wifi(){
    conf=$1 && ssid=$2 && serial=$3
    if [ -z "${conf}" ]; then
        return
    fi
    ADB_OPTION=""
    if [ -n "${serial}" ]; then
        ADB_OPTION="-s ${serial}"
    fi

    adb ${ADB_OPTION} shell am start -a android.intent.action.MAIN -n com.android.settings/.Settings
    sleep 3
    adb ${ADB_OPTION} shell service call wifi 13 i32 0
    sleep 5
    adb ${ADB_OPTION} push "${conf}" /data/misc/wifi/wpa_supplicant.conf
    adb ${ADB_OPTION} shell chown wifi.wifi /data/misc/wifi/wpa_supplicant.conf
    adb ${ADB_OPTION} shell chmod 660 /data/misc/wifi/wpa_supplicant.conf
    adb ${ADB_OPTION} shell ls -l /data/misc/wifi/wpa_supplicant.conf
    adb ${ADB_OPTION} shell service call wifi 13 i32 1
    #extend the wait time because the time to turn wifi on some devices(like
    #Origen) will take a little longer
    sleep 60
    for i in {1..30}; do
        adb ${ADB_OPTION} shell wpa_cli list_networks|grep -E "^\s*[[:digit:]]+\s+${ssid}\s+any\s+\[CURRENT\]"
        if [ $? -eq 0 ];then
            break
        fi
        sleep 5
    done

    if [ $i -eq 30 ]; then
        echo "connect-lava-wifi-${ssid}=fail"
        return 1
    else
        echo "connect-lava-wifi-${ssid}=pass"
        return 0
    fi
}

function parse_argv() {
    # Parse command line arguments
    # Sets: VERBOSE, dev
    while test -n "$1"; do
        case "$1" in
            --serial|-s)
                SERIAL="$2"
                shift 2
                ;;
            --passwd|-p)
                PASSWD="$2"
                shift 2
                ;;
            *)
                if [ -n "${SSID}" ]; then
                    show_usage
                    exit 1
                else
                    SSID="$1"
                    shift
                fi
                ;;
        esac
    done
}

function show_usage(){
    # Display the usage line
    echo "Usage 1, Specify the ssid and pawword via command line:"
    echo "    $0 [--passwd|-p passwd] [--serial|-s serial] ssid"
    echo "Usage 2, Specify the ssid and pawword via configuration file:"
    echo "    Specify the file path via 'WIFI_DEV_CONF' environment variable,"
    echo "    /etc/lava/devices/wifi.conf is the default value if not specified"
    echo "    The content of this file like this:"
    echo "    SSID=the ssid of wifi"
    echo "    PASSWD=the password of the specified wifi via SSID"
}

function main(){
    if [ -z "${WIFI_DEV_CONF}" ]; then
        wifi_dev_conf="/etc/lava/devices/wifi.conf"
    else
        wifi_dev_conf="${WIFI_DEV_CONF}"
    fi

    echo "Will use ${wifi_dev_conf} as the configuration file for wifi if exists"
    if [ -f "${wifi_dev_conf}" ]; then
        . "${wifi_dev_conf}"
    fi
    parse_argv "$@"

    if [ -z "${SSID}" ]; then
        show_usage
        exit 1
    fi

    wifi_conf="wpa_supplicant.conf"
    generate_wpa_conf "${wifi_conf}" "${SSID}" "${PASSWD}"
    enable_wifi "${wifi_conf}" "${SSID}" "${SERIAL}"
    RET=$?
    rm -f "${wifi_conf}"
    exit $RET
}

main "$@"

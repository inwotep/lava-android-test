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

#the default ip or domain used by the client to access the server
DEFAULT_DOMAIN_IP='192.168.1.10'
DEFAULT_BROWSER='DEFAULT'

########################################################
######        NOT MODIFY SOURCE OF BELOW           #####
########################################################
THIS_FILE="$0"
methanol_git="git://github.com/szeged/methanol.git"
chrome_apk_url="http://testdata.validation.linaro.org/chrome/Chrome-latest.apk"
server_settings_file="/etc/lava/web_server/settings.conf"
result_dir_android="/data/local/methanol"
declare -a RESULTS=();
methanol_url="/"
report_url="/cgi/save_methanol_data.py"
report_res_dir="/tmp/methanol"
target_dir=""
server_pid=""

ADB_OPTION=""
domain_ip="${DEFAULT_DOMAIN_IP}"
browser="${DEFAULT_BROWSER}"
test_target=""

function parse_arg(){
    serial=""
    while test -n "$1"; do
        case "$1" in
            --browser|-b)
                if [ "x$2" = "x" ]; then
                    echo "Error: $1 requires an argument which should be DEFAULT or CHROME"
                    exit 1
                fi
                browser="$2"
                if [ "X${browser}" != "XDEFAULT" ] && [ "X${browser}" != "XCHROME" ]; then
                    echo "Error: $1 requires an argument  which should be DEFAULT or CHROME"
                    exit 1
                fi
                shift 2
                ;;
            --domain|-d)
                if [ "x$2" = "x" ]; then
                    echo "Error: $1 requires an argument"
                    exit 1
                fi
                domain_ip="$2"
                shift 2
                ;;
            --target|-t)
                if [ "x$2" = "x" ]; then
                    echo "Error: $1 requires an argument"
                    exit 1
                fi
                test_target="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                if [ -n "${serial}" ]; then
                    show_usage
                    echo "Too many arguments, see --help for details"
                    exit 1
                else
                    serial="$1"
                    shift
                fi
                ;;
        esac
    done

    if [ -n "${serial}" ]; then
        ADB_OPTION="-s ${serial}"
    fi
}

function show_usage(){
    echo "`basename ${THIS_FILE}` [serial_no] [-b DEFAULT|CHROME] [-d domain_ip]"
}

function patch_sources(){
    src_root_dir=${1}
    if [ -z ${src_root_dir} ]; then
        return
    fi

    if [ \! -d ${src_root_dir} ]; then
        return
    fi

    ## The following test case cannot be on android browser, so comment them out
    ## Patch the engine.js
    sed -i "s% + results;% + results.replace\(new RegExp('/','gm'), '_'\);%" ${src_root_dir}/engine.js

    ##Patch svg.js
    sed -i s%\"svg/anim/earth.svg\",%\"svg/anim/earth.svg\"/*,%    ${src_root_dir}/svg.js
    sed -i s%\"svg/anim/svg.svg\"%\"svg/anim/svg.svg\"*/%    ${src_root_dir}/svg.js

    ##Patch smp.js
    sed -i s%\"smp/3d-terrain-demo/single/index.html\",%//\"smp/3d-terrain-demo/single/index.html\",%   ${src_root_dir}/smp.js
    sed -i s%\"smp/3d-terrain-demo/worker/index.html\",%//\"smp/3d-terrain-demo/worker/index.html\",%   ${src_root_dir}/smp.js
    sed -i s%\"smp/fire-on-water/worker/index.html\",%//\"smp/fire-on-water/worker/index.html\",%   ${src_root_dir}/smp.js
}

function deploy(){

    if [ "${browser}" = "CHROME" ]; then
        echo "wget --progress=dot -e dotbytes=1M -np -l 10 --no-check-certificate ${chrome_apk_url} -O ./Chrome-latest.apk"
        wget --progress=dot -e dotbytes=1M -np -l 10 --no-check-certificate ${chrome_apk_url} -O ./Chrome-latest.apk
        if [ $? -ne 0 ]; then 
            echo "Failed to download the chrome apk file from ${chrome_apk_url}."
            cleanup
            exit 1
        fi

        adb ${ADB_OPTION} uninstall com.android.chrome

        echo "adb ${ADB_OPTION} install ./Chrome-latest.apk"
        adb ${ADB_OPTION} install ./Chrome-latest.apk
        if [ $? -ne 0 ]; then 
            echo "Failed to install the Chrome browser application."
            cleanup
            rm -f ./Chrome-latest.apk
            exit 1
        fi
        rm -f ./Chrome-latest.apk
        adb ${ADB_OPTION} shell am start com.android.chrome/com.google.android.apps.chrome.Main
        sleep 10
        f_preferences='/data/data/com.android.chrome/shared_prefs/com.android.chrome_preferences.xml'
        f_preferences_base=`basename ${f_preferences}`
        owner_grp=`adb ${ADB_OPTION} shell ls -l ${f_preferences}|cut -d \  -f2`
        if [ -z "${owner_grp}" ]; then
            echo "Failed to get the user/group infromation of chrome preferences file."
            cleanup
            rm -f ./Chrome-latest.apk
            exit 1
        fi
        adb ${ADB_OPTION} pull ${f_preferences} ./${f_preferences_base}
        sed -i '/<map>/ a\<boolean name="first_run_flow" value="true" />' ./${f_preferences_base}
        adb ${ADB_OPTION} push ./${f_preferences_base} ${f_preferences}
        adb ${ADB_OPTION} shell chown ${owner_grp}:${owner_grp} ${f_preferences}
        chrome_pid=`adb ${ADB_OPTION} shell ps |grep -P 'chrome\s*$'|tr -s ' '|cut -d \  -f2`
        if [ -n "${chrome_pid}" ]; then
            adb ${ADB_OPTION} shell kill ${chrome_pid}
        fi
        rm -f ./${f_preferences_base}
    fi

    cur_path=`pwd`
    target_dir=`mktemp -u --tmpdir=${cur_path} methanol-XXX`
    git clone "${methanol_git}" "${target_dir}"
    if [ $? -ne 0 ];then
        echo "Failed to clone the methanol source from ${methanol_git}"
        cleanup
        exit 1
    fi

    #patch just because some test can not be run on android
    patch_sources "${target_dir}"

    url_file=`mktemp -u --tmpdir=${cur_path} url-XXX`
    nohup python `dirname $0`/start_server.py "${domain_ip}" "${target_dir}" "${url_file}" &>server.log &
    server_pid=$!
    sleep 5
    domain_protocol=`cat ${url_file}`
    if [ -z "${domain_protocol}" ]; then
        echo "Cannot get the url of the temporary created server."
        echo "Failed to deploy the temporary server"
        cleanup
        exit 1
    fi
}

function check_url(){
    if [ -n "${report_url}" ]; then
        wget -q "${domain_protocol}/${report_url}" -O /dev/null
        if [ $? -ne 0 ]; then
            echo "The report url(${domain_protocol}/${report_url}) cannot be accessed"
            echo "Please put the save_methanol_data.py to the cgi-bin directory"
            echo "of your web server, and make sure it is accessible."
            cleanup
            exit 1
        fi
    fi

    if [ -n "${methanol_url}" ]; then
        wget -q "${domain_protocol}/${methanol_url}" -O /dev/null
        if [ $? -ne 0 ]; then
            echo "The url(${domain_protocol}/${methanol_url}) cannot be accessed"
            echo "Please clone the methanol directory to local via following command"
            echo "    git clone ${methanol_git}"
            echo "and copy the entire directory to some place of your web server"
            echo "and make sure it is accessible."
            cleanup
            exit 1
        fi
    else
        echo "Please speecify the methanol url that will be used for test."
        cleanup
        exit 1
    fi
}

function wait_result(){
    if [ -n "$1" ]; then
        file_path="$1"
    else
        return 0
    fi

    for (( i=1; ; i++ )); do
        sleep 300
        if [ -f "${file_path}" ]; then
            return 0
        fi
    done
    return 1
}

function test_methanol(){
    if [ -n "$1" ]; then
        test_type="-${1}"
    else
        test_type=""
    fi

    result_file=`mktemp -u --tmpdir=${report_res_dir} fire${test_type}-XXX.json`
    res_basename=`basename ${result_file}`
    test_url="${domain_protocol}/${methanol_url}/fire${test_type}.html"
    if [ -n "${report_url}" ]; then
        test_url="${test_url}?reportToUrl=${report_url}%3Fsave2file=${res_basename}"
    fi

    component_default="com.android.browser/.BrowserActivity"
    component_chrome=" com.android.chrome/com.google.android.apps.chrome.Main"
    if [ "${browser}" = "CHROME" ]; then
        component=${component_chrome}
    else
        component=${component_default}
    fi
    echo "adb ${ADB_OPTION} shell am start -a android.intent.action.VIEW -d ${test_url} -n ${component}"
    adb ${ADB_OPTION} shell "am start -a android.intent.action.VIEW -d ${test_url} -n ${component}"
    wait_result "${result_file}"
    if [ $? -eq 0 ]; then
        cur_path=`pwd`
        cp -uvf ${result_file}  ${cur_path}/${res_basename}
        echo "result_file=${cur_path}/${res_basename}"
        RESULTS[${#RESULTS[@]}]="${cur_path}/${res_basename}"

        rm -f ${result_file}
    else
        echo "Failed to get the test result of fire${test_type}.html"
        #cleanup
        #exit 1
    fi
}

function cleanup(){
    echo "DO CLEAN UP"
    rm -fr methanol_result.json "${RESULTS[@]}"
    if [ -n "${server_pid}" ]; then
        kill -9 ${server_pid}
    fi
    if [ -n "${target_dir}" ]; then
        rm -fr "${target_dir}"
    fi
    if [ "${browser}" = "CHROME" ]; then
        adb ${ADB_OPTION} uninstall com.android.chrome
    fi
}

function main(){
    parse_arg "$@"

    ## delete the test result for last time
    adb ${ADB_OPTION} shell rm "${result_dir_android}/methanol_result.json"

    trap cleanup EXIT

    deploy

    check_url

    page_suffix='${test_target}'
    if [ -n "${page_suffix}" ]; then
        page_suffix="-${test_target}"
    fi
    echo `date`: starts to test fire${page_suffix}.html
    test_methanol "${test_target}"
    echo `date`: all tests completed

    echo "Merge results of file: ${RESULTS[@]}"
    `dirname $0`/methanol_merge_results.py methanol_result.json "${RESULTS[@]}"
    if [ $? -eq 0 ]; then
        adb ${ADB_OPTION} shell mkdir ${result_dir_android}
        adb ${ADB_OPTION} push methanol_result.json "${result_dir_android}/methanol_result.json"
        for f in "${RESULTS[@]}"; do
            adb ${ADB_OPTION} push "${f}" "${result_dir_android}"
        done
        echo "The result is also push to android: ${result_dir_android}/${res_basename}"
    else
        echo "Failed to merge the results"
    fi
}
main "$@"

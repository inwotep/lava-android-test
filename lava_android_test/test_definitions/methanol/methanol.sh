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

# group1: if we need to copy the test web pages to the webpage directory 
#        of local web server, or copy the cgi script for report to the 
#        cgi directory of local web server via this script, 
#        then we should specify the following variables of group1. 
#        and the variables of #group2 will be set by this script automatically,
#        therefor no need to define them.
# webpages_url and webpages_dir:
#        when copie the cloned methanol directory to ${webpages_dir}, 
#        we should be able to access it via ${webpages_url}/methanol from android
# cgi_url and cgi_dir:
#        when copied the cgi script(e.g. save_methanol_data.py) for reporting 
#        result to ${cgi_dir}, 
#        we should be able to access it via ${cgi_url}/save_methanol_data.py from android
domain_protocol='http://192.168.1.10/'
webpages_url="/images/"
webpages_dir="/linaro/images/"
cgi_url="/cgi-bin/"
cgi_dir="/usr/lib/cgi-bin/"

# group2: if we have the fixed url for report_url and webpage url
#        then we can only define the following variables.
#        no need to define the above #group1 variables
# methanol_url: the url to access the webpages. like:
#           methanol_url="http://127.0.0.1/methanol"
#           methanol_url="file:///sdcard/methanol"
# report_url: the url to report result data. like:
#           report_url="http://127.0.0.1/cgi-bin/save_methanol_data.py"
methanol_url=""
report_url=""

########################################################
######        NOT MODIFY SOURCE OF BELOW           #####
########################################################
#android_dir="/sdcard/methanol"
methanol_git="git://gitorious.org/methanol/methanol.git"
server_settings_file="/etc/lava/web_server/settings.conf"
result_dir_android="/data/local/methanol"
declare -a RESULTS=();
target_web_dir=""
target_cgiscript_path=""

SERIAL=${1-""}
ADB_OPTION=""
if [ -n "${SERIAL}" ]; then
    ADB_OPTION="-s ${SERIAL}"
fi

function patch_sources(){
    src_root_dir=${1}
    if [ -z ${src_root_dir} ]; then
        return
    fi

    if [ \! -d ${src_root_dir} ]; then
        return
    fi

    ## The following test case cannot be on android browser, so comment them out

    ##Patch svg.js
    sed -i s%\"svg/anim/earth.svg\",%\"svg/anim/earth.svg\"/*,%    ${src_root_dir}/svg.js
    sed -i s%\"svg/anim/svg.svg\"%\"svg/anim/svg.svg\"*/%    ${src_root_dir}/svg.js

    ##Patch smp.js
    sed -i s%\"smp/3d-terrain-demo/single/index.html\",%//\"smp/3d-terrain-demo/single/index.html\",%   ${src_root_dir}/smp.js
    sed -i s%\"smp/3d-terrain-demo/worker/index.html\",%//\"smp/3d-terrain-demo/worker/index.html\",%   ${src_root_dir}/smp.js
    sed -i s%\"smp/fire-on-water/worker/index.html\",%//\"smp/fire-on-water/worker/index.html\",%   ${src_root_dir}/smp.js
}

function deploy(){
    cur_path=`pwd`
    target_dir=`mktemp -u --tmpdir=${cur_path} methanol-XXX`
    git clone "${methanol_git}" "${target_dir}"
    if [ $? -ne 0 ];then
        echo "Faile to clone the methanol source from ${methanol_git}"
        cleanup
        exit 1
    fi

    #patch just because some test can not be run on android
    patch_sources "${target_dir}"

    if [ -n "${webpages_dir}" ]; then
        target_web_dir=`mktemp -u --tmpdir=${webpages_dir} methanol-XXX`
        target_web_dir_basename=`basename ${target_web_dir}`
        sudo cp -r "${target_dir}" "${target_web_dir}"
        sudo chmod -R +r "${target_web_dir}"
        target_web_dir_basename=`basename ${target_web_dir}`
        methanol_url="${webpages_url}/${target_web_dir_basename}"
    else
        adb ${ADB_OPTION} push "${target_dir}" "${android_dir}"
    fi

    #copy the file to the cgi-bin directory
    if [ -n "${cgi_dir}" ]; then
        target_cgiscript_path=`mktemp -u ${cgi_dir}/save_methanol_data_XXX.py`
        sudo cp -uvf "${target_dir}/cgi/save_methanol_data.py" "${target_cgiscript_path}"
        sudo chmod +x ${target_cgiscript_path}
        script_basename=`basename ${target_cgiscript_path}`
        report_url="${cgi_url}/${script_basename}"
    fi

    rm -fr ${target_dir}
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
    wait_minutes=${2-1}

    for (( i=1; i<=${wait_minutes}; i++ )); do
        sleep 60
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

    wait_minutes=${2-1}

    mkdir -p /tmp/methanol/
    sudo chmod -R 777 /tmp/methanol
    result_file=`mktemp -u --tmpdir=/tmp/methanol fire${test_type}-XXX.json`
    res_basename=`basename ${result_file}`
    test_url="${domain_protocol}/${methanol_url}/fire${test_type}.html"
    if [ -n "${report_url}" ]; then
        test_url="${test_url}?reportToUrl=${report_url}%3Fsave2file=${res_basename}"
    fi

    echo "adb ${ADB_OPTION} shell am start -a android.intent.action.VIEW -d ${test_url}"
    adb ${ADB_OPTION} shell "am start -a android.intent.action.VIEW -d ${test_url}"
    wait_result "${result_file}" ${wait_minutes}
    if [ $? -eq 0 ]; then
        cur_path=`pwd`
        cp -uvf ${result_file}  ${cur_path}/${res_basename}
        echo "result_file=${cur_path}/${res_basename}"
        RESULTS[${#RESULTS[@]}]="${cur_path}/${res_basename}"

        rm -f ${result_file}
    else
        echo "Failed to get the test result of fire${test_type}.html"
        cleanup
        exit 1
    fi
}

function cleanup(){
    sudo rm -fr methanol_result.json "${RESULTS[@]}"
    if [ -n "${webpages_dir}" ]; then
        sudo rm -fr "${target_web_dir}"
    fi
    if [ -n "${cgi_dir}" ]; then
        sudo rm -fr "${target_cgiscript_path}"
    fi
}

function main(){
    trap cleanup EXIT

    if [ -n "${WEB_SERVER_SEETINGS_CONF}" ]; then
        server_settings_file="${WIFI_DEV_CONF}"
    fi

    echo "Will use ${server_settings_file} as the configuration file for web server"
    if [ -f "${server_settings_file}" ]; then
        . "${server_settings_file}"
    fi

    deploy

    check_url
    test_methanol "" 20
    test_methanol "svg" 20
    test_methanol "smp" 20

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
        echo "Failed to merege the results"
        cleanup
        exit 1
    fi
    cleanup
}
main "$@"

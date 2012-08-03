#!/bin/bash


#android_dir="/sdcard/methanol"
#methanol_url="file://${android_dir}"
webpages_url="http://192.168.1.127/images/"
webpages_dir="/var/www/images"
cgi_url="http://192.168.1.127/cgi-bin/"
cgi_dir="/usr/lib/cgi-bin/"
########################################################
######        NOT MODIFY SOURCE OF BELOW           #####
########################################################
#methanol_git="git://gitorious.org/methanol/methanol.git"
methanol_git="git@gitorious.org:~liuyq0307/methanol/liuyq0307s-methanol.git"
target_web_dir=""
target_cgiscript_path=""
methanol_url=""
report_url=""

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
        exit 1
    fi

    patch_sources "${target_dir}"

    if [ -n "${webpages_dir}" ]; then
        target_web_dir=`mktemp -u --tmpdir=${webpages_dir} methanol-XXX`
        cp -r "${target_dir}" "${target_web_dir}"
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
        wget -q "${report_url}" -O /dev/null
        if [ $? -ne 0 ]; then
            echo "The report url(${report_url}) cannot be accessed"
            echo "Please put the save_methanol_data.py to the cgi-bin directory"
            echo "of your web server, and make sure it is accessible."
            exit 1
        fi
    fi

    if [ -n "${methanol_url}" ]; then
        wget -q "${methanol_url}" -O /dev/null
        if [ $? -ne 0 ]; then
            echo "The url(${methanol_url}) cannot be accessed"
            echo "Please clone the methanol directory to local via following command"
            echo "    git clone ${methanol_git}"
            echo "and copy the entire directory to some place of your web server"
            echo "and make sure it is accessible."
            exit 1
        fi
    else
        echo "Please speecify the methanol url that will be used for test."
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
    result_file=`mktemp -u --tmpdir=/tmp/methanol res${test_type}-XXX.json`
    res_basename=`basename ${result_file}`
    test_url="${methanol_url}/fire${test_type}.html"
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
        rm -f ${result_file}
    else
        echo "Failed to get the test result of fire${test_type}.html"
        exit 1
    fi
}

function cleanup(){
    if [ -n "" ]; then
        sudo rm -fr "${target_web_dir}"
    fi
    if [ -n "" ]; then
        sudo rm -fr "${target_cgiscript_path}"
    fi
}

function main(){
    trap cleanup EXIT

    deploy

    check_url
    test_methanol "" 1
    test_methanol "svg" 5
    test_methanol "smp" 20

    exit 0
}
main "$@"

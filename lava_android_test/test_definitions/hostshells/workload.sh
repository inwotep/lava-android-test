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

function parse_argv() {
    # Parse command line arguments
    while test -n "$1"; do
        case "$1" in
            --serial|-s)
                SERIAL="$2"
                if [ -n "${SERIAL}" ]; then
                    shift 2
                else
                    show_usage
                    exit 1
                fi
                ;;
            --config|-c)
                CONFIG="$2"
                if [ -n "${CONFIG}" ]; then
                    shift 2
                else
                    show_usage
                    exit 1
                fi
                ;;
            --git|-g)
                GIT_URL="$2"
                if [ -n "${GIT_URL}" ]; then
                    shift 2
                else
                    show_usage
                    exit 1
                fi
                ;;
            --help|-h)
                show_usage
                exit 1
                ;;
            *)
                if [ -n "${OPTIONS}" ]; then
                    OPTIONS="${OPTIONS} $1"
                else
                    OPTIONS="$1"
                fi
                shift
                ;;
        esac
    done
}

function show_usage(){
    # Display the usage line
    echo "Usage $(basename $0) [--serial|-s <serial>] [--config|-c <config_file>] [--git|g <git-url>] <other-option>"
    echo "Usage $(basename $0) [--help|-h]"
}

function parse_output_result(){
    result_f=${1}
    if [ ! -f "${1}" ]; then
        echo "There is no result file output/results.csv"
        return
    fi

    file_tmp=${result_f}.tmp
    sed 's/ /_/g'  ${result_f} > ${file_tmp}
    keys=`head -n 1 ${file_tmp}`
    values=`tail -n 1 ${file_tmp}`
    for ((i=1; i<21; i++)); do
        key=`echo ${keys}|cut -d , -f ${i}|sed 's/\r//'`
        value=`echo ${values}|cut -d , -f ${i}|sed 's/\r//'`

       echo ${value}|grep -P '^[.\d]+$' &>/dev/null
       if [ $? -ne 0 ]; then
            key="${key}_${value}"
            value="true"
        fi
        echo ${key}=${value}
    done
    rm -f ${file_tmp}
}

function main(){
    local_git="file:///home/bhoj/workload-automation.git"
    branch="lava"
    outputdir="outputdir"
    result="${outputdir}/result.csv"

    parse_argv "$@"

    config_file="config.csv"
    if [ -n "${CONFIG}" ]; then
        config_file="${CONFIG}"
    fi

    if [ -n "${GIT_URL}" ]; then
        git_url="${GIT_URL}"
    else
        git_url="${local_git}"
    fi

    git clone "${git_url}" -b ${branch}
    if [ $? -ne 0 ]; then
        echo "Failed to clone git repository: ${git_url}"
        exit 1
    fi
    ip=`echo ${SERIAL}|sed 's/:5555//'`
    cd "workload-automation"

    #update the ip address and patch config.csv file
    sed -i "s/192.168.1.38/${ip}/g" workload_config.py

    python workload_setup_dependencies.py
    if [ $? -ne 0 ]; then
        echo "Failed to run workload_setup_dependencies.py"
        exit 1
    fi

    rm -fr ${outputdir}
    python workload.py ${config_file} ${outputdir}/
    if [ $? -ne 0 ]; then
        echo "Failed to run workload.py config.csv outputdir/"
        exit 1
    fi
    parse_output_result ${result}
}

main "$@"


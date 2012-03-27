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

ADB_CMD="adb"
prog_dir=`dirname $0`

function main(){
    if [ "x${1}" != "x" ]; then
        ADB_CMD="${ADB_CMD} -s ${1}"
    fi
    ${ADB_CMD} logcat -c
    ${ADB_CMD} shell am start -W org.linaro.glmark2/.Glmark2Activity
    python ${prog_dir}/glmark2_wait.py ${1}
    #${ADB_CMD} logcat -d glmark2:I *:S
    ${ADB_CMD} logcat -d
}

main "$@"

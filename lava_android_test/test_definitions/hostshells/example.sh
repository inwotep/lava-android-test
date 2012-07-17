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
                    shift 1
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
    echo "Usage $0 [--serial|-s serial] other-option"
    echo "Usage $0 [--help|-h]"
}

function main(){
    parse_argv "$@"
    echo "hostshells-example-fail=fail"
    echo "hostshells-example-pass=pass"
}

main "$@"
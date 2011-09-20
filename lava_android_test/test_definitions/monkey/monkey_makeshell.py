# Copyright (c) 2011 Linaro

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
#
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
import os
from lava_android_test.config import get_config

config = get_config()
monkey_sh_temp_path = os.path.join(config.tempdir_host, 'monkey.sh')
with open(monkey_sh_temp_path, 'w') as fd:
    fd.write('#!/system/bin/sh\n')
    fd.write('monkey_cmd="monkey -s 1 --pct-touch 10 --pct-motion 20 --pct-nav 20 --pct-majornav 30 --pct-appswitch 20 --throttle 500 100"\n')
    fd.write("echo execute command=${monkey_cmd}\n")
    fd.write("${monkey_cmd}\n")
    fd.write("echo MONKEY_RET_CODE=$?\n")
fd.close()

# Copyright (C) 2012 Linaro Limited
#
# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.

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
import subprocess

from lava_android_test import utils


class RepositoryError(Exception):
    """
    Raise this for repository related errors
    """


class Repository(object):
    '''
    Base class for all repository class used to checkout files.
    This class and sub classes are base the repository command.
    '''

    def __init__(self, url, repo_type, cmds=[]):
        self.url = url
        self.repo_type = repo_type
        self.check_cmds_exist(cmds)

    def checkout(self, target_dir=None):
        """
        Checkout this repository to the specified the target_dir directory
        """
        raise NotImplementedError()

    def check_cmds_exist(self, cmds=[]):
        """
        check whether the necessary commands are existing.
        """
        for cmd in cmds:
            if not utils.check_command_exist(cmd):
                raise RepositoryError(("The necessary command(%) does not"
                                      " exist, Or can't be seen from path")
                                       % cmd)


class GitRepository(Repository):

    git_cmd = 'git'

    def __init__(self, url):
        super(GitRepository, self).__init__(url, 'git', [self.git_cmd])

    def checkout(self, target_dir=None):
        """
        Checkout this git repository to the specified the target_dir directory
        """
        cmds = []
        if not target_dir:
            cmds = [self.git_cmd, 'clone', self.url]

        else:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            cmds = [self.git_cmd, 'clone', self.url, target_dir]

        rc = subprocess.call(cmds)
        if rc != 0:
            raise RepositoryError(("Failed to clone the specified "
                  "repository() with exist staus=%d")
                                   % (self.url, rc))

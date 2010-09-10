# Copyright (c) 2010 Linaro
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

import base64
import os
import sys
from ConfigParser import ConfigParser, NoOptionError
from getpass import getpass
from optparse import make_option

from abrek.command import AbrekCmd
from abrek.config import get_config


class DashboardConfig(object):
    """
    Read and write dashboard configuration data
    """

    def __init__(self, section="Default Server"):
        self.dashboardconf = ConfigParser()
        self.section = section
        self.config = get_config()
        self.path = os.path.join(self.config.configdir, "dashboard.conf")
        if os.path.exists(self.path):
            self.dashboardconf.read(self.path)
        if not (self.section in self.dashboardconf.sections()):
            self.dashboardconf.add_section(self.section)

    def set_host(self, host):
        self.dashboardconf.set(self.section, 'host', host)

    def get_host(self):
        try:
            host = self.dashboardconf.get(self.section, 'host')
            return host
        except NoOptionError:
            return ""

    host = property(get_host, set_host)

    def set_user(self, user):
        self.dashboardconf.set(self.section, 'user', user)

    def get_user(self):
        try:
            user = self.dashboardconf.get(self.section, 'user')
            return user
        except NoOptionError:
            return ""

    user = property(get_user, set_user)

    def set_password(self, password):
        #Not exactly secure, but better than storing in plaintext
        password = base64.encodestring(password).strip()
        self.dashboardconf.set(self.section,'password', password)

    def get_password(self):
        try:
            password = self.dashboardconf.get(self.section, 'password')
            return base64.decodestring(password)
        except NoOptionError:
            return ""

    password = property(get_password, set_password)

    def write(self):
        """
        write the dashboard configuration out to the config file
        """
        if not os.path.exists(self.config.configdir):
            os.makedirs(self.config.configdir)
        with open(self.path, "w") as fd:
            self.dashboardconf.write(fd)


class subcmd_dashboard_setup(AbrekCmd):
    """
    Configure information needed to push results to the dashboard
    """
    options = [make_option("-u", "--user", dest="user"),
               make_option("-p", "--password", dest="password")]
    arglist = ["*server"]

    def run(self):
        if len(self.args) != 1:
            print "You must specify a server"
            sys.exit(1)
        config = DashboardConfig()
        if self.opts.user:
            user = self.opts.user
        else:
            user = raw_input("Username: ")
        if self.opts.password:
            password = self.opts.password
        else:
            password = getpass()
        config.host = self.args[0]
        config.user = user
        config.password = password
        config.write()


class cmd_dashboard(AbrekCmd):
    """
    Connect to the Launch-control dashboard
    """
    subcmds = {'setup':subcmd_dashboard_setup()}

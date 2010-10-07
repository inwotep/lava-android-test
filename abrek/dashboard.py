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
import json
import os
import sys
import urllib
import xmlrpclib
from ConfigParser import ConfigParser, NoOptionError
from getpass import getpass
from optparse import make_option

from abrek.command import AbrekCmd
from abrek.config import get_config
from abrek.testdef import testloader


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


class subcmd_dashboard_put(AbrekCmd):
    """
    Push the results from a test to the server
    The stream name must include slashes (e.g. /anonymous/foo/)
    """
    arglist = ["*stream", "*result"]

    def run(self):
        if len(self.args) != 2:
            print "You must specify a stream and a result"
            sys.exit(1)
        stream_name = self.args[0]
        result_name = self.args[1]
        bundle = generate_bundle(result_name)
        db_config = DashboardConfig()
        hosturl = urllib.basejoin(db_config.host, "xml-rpc/")
        try:
            server = xmlrpclib.Server(hosturl)
        except IOError:
            print "Error connecting to server, please run 'abrek " \
                "dashboard setup [host]'"
            sys.exit(1)
        try:
            result = server.put(json.dumps(bundle, indent=2), result_name,
                stream_name)
            print "Bundle successfully uploaded to id: %s" % result
        except xmlrpclib.Fault as strerror:
            print "Error uploading bundle: %s" % strerror.faultString
            sys.exit(1)


class subcmd_dashboard_bundle(AbrekCmd):
    """
    Print JSON output that can be imported into the dashboard
    """
    arglist = ["*result"]

    def run(self):
        if len(self.args) != 1:
            print "You must specify a result"
            sys.exit(1)
        bundle = generate_bundle(self.args[0])
        print json.dumps(bundle, indent=2)


def generate_bundle(result):
    config = get_config()
    resultdir = os.path.join(config.resultsdir, result)
    if not os.path.exists(resultdir):
        print "Result directory not found"
        sys.exit(1)
    testdatafile = os.path.join(resultdir, "testdata.json")
    testdata = json.loads(file(testdatafile).read())
    test = testloader(testdata['test_runs'][0]['test_id'])
    try:
        test.parse(result)
    except Exception as strerror:
        print "Test parse error: %s" % strerror
        sys.exit(1)
    testdata['test_runs'][0].update(test.parser.results)
    return testdata


class cmd_dashboard(AbrekCmd):
    """
    Connect to the Launch-control dashboard
    """
    subcmds = {'bundle':subcmd_dashboard_bundle(),
               'put':subcmd_dashboard_put(),
               'setup':subcmd_dashboard_setup()}

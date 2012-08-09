#/usr/bin/python
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

import os
import sys
import CGIHTTPServer
import BaseHTTPServer

### check parameter
if len(sys.argv) < 3:
    print 'Please spsecify the ip and directory like this:'
    print '    %s domain-or-ip directory-path url-file' % (
                                                   os.path.basename(__file__))
    sys.exit(1)

domain = sys.argv[1]
directory = sys.argv[2]
if len(sys.argv) == 4:
    url_file = sys.argv[3]
else:
    url_file = ''

## change to that directory
old_dir = os.getcwd()
os.chdir(directory)

## set the server configuration before start
cgi_handler = CGIHTTPServer.CGIHTTPRequestHandler
cgi_handler.cgi_directories.append('/cgi')
httpd = BaseHTTPServer.HTTPServer((domain, 0), cgi_handler)
url = '%s://%s:%s/' % ('http', httpd.socket.getsockname()[0],
                        httpd.socket.getsockname()[1])

## out put the url information to console and file for other script reference
print "serving at url=", url
if url_file:
    with open(url_file, 'w') as stream:
        stream.write(url)
        print 'The information of url also have been wirtten into file(%s)' % (
                                    url_file)

try:
    httpd.serve_forever()
finally:
    os.chdir(old_dir)

# Copyright (c) 2011 Linaro
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

"""
This module attempts to use the linaro-dashboard-bundle package, if possible.

Using that package adds proper support for loading and saving bundle
documents.  In particular it supports loosles decimals, better, more stable
load-modify-write cycles, data validation, transparent migration and many
other features.

It is not a hard dependency to make it possible to run abrek from a checkout
without having to install (too many) dependencies.
"""

try:
    from linaro_dashboard_bundle import DocumentIO
except ImportError:
    import json

    class DocumentIO(object):
        """ Bare replacement DocumentIO without any fancy features """

        @classmethod
        def dumps(cls, doc):
            return json.dumps(doc, indent=2)

        @classmethod
        def loads(cls, text):
            doc = json.loads(text)
            fmt = doc.get("format")
            return fmt, doc
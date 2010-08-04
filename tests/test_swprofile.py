import unittest

import abrek.swprofile

class Version:
    def __init__(self, version):
        self.version = version

class Package:
    def __init__(self, name, version, is_installed=True):
        self.is_installed = is_installed
        self.name = name
        self.installed = Version(version)

class AptCache:
    def __init__(self, packages=[]):
        self.packages = packages

    def __iter__(self):
        return iter(self.packages)

class SwprofileTests(unittest.TestCase):
    def setUp(self):
        self.lsb_desc = 'test description'
        self.lsb_information = {'DESCRIPTION':self.lsb_desc}
        self.testpackage = Package('testpkg', '7.77')
        self.cache = AptCache([self.testpackage])

    def make_profile(self, test_id='unit', cache=None, info=None):
        if cache == None:
            cache = self.cache
        if info == None:
            info = self.lsb_information
        return abrek.swprofile.get_sw_context(test_id, apt_cache=cache,
                lsb_information=info)

    def test_pkg_name(self):
        a = self.make_profile()
        for pkg in a['packages']:
            self.assertEqual(self.testpackage.name, pkg['name'])

    def test_pkg_version(self):
        a = self.make_profile()
        for pkg in a['packages']:
            self.assertEqual(self.testpackage.installed.version, pkg['version'])

    def test_image_desc(self):
        a = self.make_profile()
        self.assertEqual(self.lsb_desc, a['sw_image']['desc'])


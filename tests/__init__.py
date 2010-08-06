import unittest

def test_suite():
    module_names = ['tests.test_builtins',
                    'tests.test_abrekcmd',
                    'tests.test_abrektestinstaller',
                    'tests.test_abrektestrunner',
                    'tests.test_abrektestparser',
                    'tests.test_swprofile',
                    'tests.test_hwprofile']
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(module_names)
    return suite

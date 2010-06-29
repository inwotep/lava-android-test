import unittest

def test_suite():
    module_names = ['tests.test_abrekcmd',
                    'tests.test_abrektestinstaller',
                    'tests.test_abrektestrunner']
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(module_names)
    return suite

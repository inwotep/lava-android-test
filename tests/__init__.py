import unittest

def test_suite():
    module_names = ['tests.test_abrekcmd',
                    'tests.test_abrektestinstaller']
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(module_names)
    return suite

import unittest

def test_suite():
    module_names = ['tests.test_abrekcmd']
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(module_names)
    return suite

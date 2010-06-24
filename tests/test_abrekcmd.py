import unittest
from abrek.command import AbrekCmd

class testAbrekCmd(unittest.TestCase):
    def test_empty_run(self):
        cmd = AbrekCmd()
        self.assertRaises(NotImplementedError, cmd.run, ['foo'])


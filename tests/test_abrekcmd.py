import unittest
from abrek.command import AbrekCmd, get_command, get_all_cmds

class testAbrekCmd(unittest.TestCase):
    def test_empty_run(self):
        cmd = AbrekCmd()
        self.assertRaises(NotImplementedError, cmd.run)

    def test_name(self):
        class cmd_test_name(AbrekCmd):
            pass
        cmd = cmd_test_name()
        self.assertEqual("test-name", cmd.name())

    def test_help(self):
        class cmd_test_help(AbrekCmd):
            """Test Help"""
            pass
        expected_str = 'Usage: abrek test-help\n\nOptions:\n  -h, ' + \
                       '--help  show this help message and exit\n\n' + \
                       'Description:\nTest Help'
        cmd = cmd_test_help()
        self.assertEqual(expected_str, cmd.help())

    def test_no_help(self):
        class cmd_test_no_help(AbrekCmd):
            pass
        expected_str = 'Usage: abrek test-no-help\n\nOptions:\n  -h, ' + \
                       '--help  show this help message and exit'
        cmd = cmd_test_no_help()
        self.assertEqual(expected_str, cmd.help())

    def test_get_command(self):
        cmd = get_command("install")
        self.assertTrue(isinstance(cmd, AbrekCmd))

    def test_get_all_cmds(self):
        cmds = get_all_cmds()
        self.assertTrue("install" in cmds)

import unittest
from abrek.command import AbrekCmd, get_command, get_all_cmds

class testAbrekCmd(unittest.TestCase):
    def test_empty_run(self):
        cmd = AbrekCmd()
        self.assertRaises(NotImplementedError, cmd.run, ['foo'])

    def test_name(self):
        class cmd_test_name(AbrekCmd):
            pass
        cmd = cmd_test_name()
        self.assertEqual(cmd.name(),"test-name")

    def test_help(self):
        cmd = AbrekCmd()
        print cmd.help()
        self.assertTrue(cmd.help())

    def test_get_command(self):
        cmd = get_command("install")
        self.assertTrue(isinstance(cmd, AbrekCmd))

    def test_get_all_cmds(self):
        cmds = get_all_cmds()
        self.assertTrue("install" in cmds)

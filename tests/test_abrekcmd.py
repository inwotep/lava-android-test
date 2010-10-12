# Copyright (c) 2010 Linaro
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

import unittest
from optparse import make_option
from abrek.command import (
    AbrekCmd,
    AbrekCmdWithSubcommands,
    get_command,
    get_all_cmds,
    )


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

    def test_arglist(self):
        expected_str = 'Usage: abrek arglist FOO'
        class cmd_arglist(AbrekCmd):
            arglist = ['*foo']
            pass
        cmd = cmd_arglist()
        self.assertTrue(expected_str in cmd.help())

    def test_options(self):
        expected_str = '-b BAR, --bar=BAR'
        class cmd_options(AbrekCmd):
            options = [make_option("-b", "--bar", dest="bar")]
            pass
        cmd = cmd_options()
        self.assertTrue(expected_str in cmd.help())

    def test_subcmds(self):
        expected_str = 'Available sub-commands:\n  foo'

        class cmd_test_subcmds(AbrekCmdWithSubcommands):
            """Help for test-subcmds."""
            class cmd_foo(AbrekCmd):
                pass
        cmd = cmd_test_subcmds()
        self.assertTrue(
            expected_str in cmd.help()
            and 'Help for test-subcmds.' in cmd.help())

    def test_subcmds_run(self):
        expected_str = "subcmd test str"

        class cmd_test_subcmds(AbrekCmdWithSubcommands):
            class cmd_foo(AbrekCmd):
                def run(self):
                    return expected_str
        cmd = cmd_test_subcmds()
        argv = ['foo']
        self.assertEqual(expected_str, cmd.main(argv))

    def test_subcmds_name(self):
        expected_str = "subcmd test str"

        class cmd_test_subcmds(AbrekCmdWithSubcommands):
            class cmd_foo(AbrekCmd):
                def run(self):
                    return expected_str
        cmd = cmd_test_subcmds().get_subcommand('foo')
        self.assertEqual('test-subcmds foo', cmd.name())

    def test_subcmds_help(self):
        expected_str = "subcmd test str"

        class cmd_test_subcmds(AbrekCmdWithSubcommands):
            class cmd_foo(AbrekCmd):
                """Help for foo."""
                def run(self):
                    return expected_str
        cmd = cmd_test_subcmds().get_subcommand('foo')
        self.assertTrue(
            'test-subcmds foo' in cmd.help()
            and 'Help for foo.' in cmd.help())

    def test_subcmd_strip_argv(self):
        """
        Make sure that the argv list is stripped after calling the subcmd
        """

        class cmd_test_subcmds(AbrekCmdWithSubcommands):
            class cmd_foo(AbrekCmd):
                def main(self, argv):
                    return len(argv)
        cmd = cmd_test_subcmds()
        argv = ['foo']
        self.assertEqual(0, cmd.main(argv))


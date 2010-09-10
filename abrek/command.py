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

from optparse import OptionParser


class _AbrekOptionParser(OptionParser):
    """
    This is just to override the epilog formatter to allow newlines
    """
    def format_epilog(self, formatter):
        return self.epilog


class AbrekCmd(object):
    """ Base class for commands that can be passed to Abrek.

    Commands added to abrek should inherit from AbrekCmd.  To allow for
    autodiscovery, the name of the class should begin with cmd_.

    Arguments allowed by the command can be specified in the 'arglist'.
    These arguments will automatically be listed in the help for that
    command.  Required arguments should begin with a '*'.  For example:
        arglist = ['*requiredarg', 'optionalarg']

    Options may also be specified by using the 'options' list.  To add
    arguments, you must use the make_option() function from optparse.
    For example:
        options = [make_option("-b", "--bar", dest="bar")]

    Commands also support subcommands.  A subcommand is similar to a
    command in abrek, and it should also inherit from AbrekCmd.  However,
    a subcommand class should not begin with cmd_.  Instead, it should
    be tied to the command that uses it, using the 'subcmds' dict.
    For example:
        class subcmd_bar(AbrekCmd):
            pass
        class cmd_foo(AbrekCmd):
            subcmds = {'bar':subcmd_bar()}
            pass
    """
    options = []
    arglist = []
    subcmds = {}

    def __init__(self):
        self.parser = _AbrekOptionParser(usage=self._usage(),
                                         epilog=self._desc())
        for opt in self.options:
            self.parser.add_option(opt)

    def main(self, argv):
        if len(argv) and argv[0] in self.subcmds.keys():
            return self.subcmds[argv[0]].main(argv[1:])
        else:
            (self.opts, self.args) = self.parser.parse_args(argv)
            return self.run()

    def name(self):
        return _convert_command_name(self.__class__.__name__)

    def run(self):
        raise NotImplementedError("%s: command defined but not implemented!" %
                                  self.name())
    def _usage(self):
        usagestr = "Usage: abrek %s" % self.name()
        for arg in self.arglist:
            if arg[0] == '*':
                usagestr += " %s" % arg[1:].upper()
            else:
                usagestr += " [%s]" % arg.upper()
        usagestr += self._list_subcmds()
        return usagestr

    def _desc(self):
        from inspect import getdoc
        docstr = getdoc(self)
        if not docstr:
            return ""
        description = "\nDescription:\n"
        description += docstr + "\n"
        return description

    def _list_subcmds(self):
        str = ""
        if self.subcmds:
            str = "\n\nSub-Commands:"
            for cmd in self.subcmds.keys():
                str += "\n  " + cmd
        return str

    def help(self):
        #For some reason, format_help includes an extra \n
        return self.parser.format_help()[:-1]

def _convert_command_name(cmd):
    return cmd[4:].replace('_','-')

def _find_commands(module):
    cmds = {}
    for name, func in module.__dict__.iteritems():
        if name.startswith("cmd_"):
            real_name = _convert_command_name(name)
            cmds[real_name] = func
    return cmds

def get_all_cmds():
    from abrek import builtins, dashboard, results
    cmds = _find_commands(builtins)
    cmds.update(_find_commands(dashboard))
    cmds.update(_find_commands(results))
    return cmds

def get_command(cmd_name):
    cmds = get_all_cmds()
    try:
        return cmds[cmd_name]()
    except KeyError:
        return None

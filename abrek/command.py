from optparse import OptionParser

class _AbrekOptionParser(OptionParser):
    """
    This is just to override the epilog formatter to allow newlines
    """
    def format_epilog(self, formatter):
        return self.epilog

class AbrekCmd(object):
    """
    Base class for commands that can be passed to Abrek.
    """
    options = []
    arglist = []

    def __init__(self):
        self.parser = _AbrekOptionParser(usage=self._usage(),
                                         epilog=self._desc())
        for opt in self.options:
            self.parser.add_option(opt)

    def main(self, argv):
        (self.opts, self.args) = self.parser.parse_args(argv)
        self.run()

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
        return usagestr

    def _desc(self):
        from inspect import getdoc
        docstr = getdoc(self)
        if not docstr:
            return ""
        description = "\nDescription:\n"
        description += docstr + "\n"
        return description

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
    import abrek.builtins
    cmds = _find_commands(abrek.builtins)
    return cmds

def get_command(cmd_name):
    cmds = get_all_cmds()
    try:
        return cmds[cmd_name]()
    except KeyError:
        return None

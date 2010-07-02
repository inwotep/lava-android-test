
class AbrekCmd(object):
    """
    Base class for commands that can be passed to Abrek.
    """
    def name(self):
        return _convert_command_name(self.__class__.__name__)

    def run(self, argv):
        raise NotImplementedError("%s: command defined but not implemented!" %
                                  self.name())
    def help(self):
        from inspect import getdoc
        print getdoc(self)

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

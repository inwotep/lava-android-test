import sys
import abrek.commands

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
        if not argv:
            argv = ['help']
        cmd = argv.pop(0)
        cmd_func = abrek.commands.get_command(cmd)
        if not cmd_func:
            print "command '%s' not found" % cmd
            return 1
        run = cmd_func.run
        run(argv)

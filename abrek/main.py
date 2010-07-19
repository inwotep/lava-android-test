import sys
import abrek.command

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
        if not argv:
            argv = ['help']
        cmd = argv.pop(0)
        cmd_func = abrek.command.get_command(cmd)
        if not cmd_func:
            print "command '%s' not found" % cmd
            return 1
        main = cmd_func.main
        main(argv)

import sys
import abrek.commands

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
        cmd = argv.pop(0)
        cmd_func = abrek.commands.get_command(cmd)
        run = cmd_func.run
        run(argv)

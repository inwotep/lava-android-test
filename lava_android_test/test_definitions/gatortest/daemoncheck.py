import sys
from commands import getstatusoutput

if len(sys.argv) == 1:
    adbcmd = 'adb'
else:
    adbcmd = 'adb -s %s' % (sys.argv[1])

cmd = '%s shell ps' % (adbcmd)
rc, output = getstatusoutput(cmd)
if rc != 0:
    print 'Failed to run command %s : %s' % (cmd, output)
    sys.exit(1)

# parse output

if output.find("gator") != -1:
    print "gator_daemon_check=pass"
else:
    print "gator_daemon_check=fail"

#!/system/bin/sh
#$1 is the testing location. The -b must be specified for parser.
#the file itself does not matter as it is not used.
#The -b cause results reports to be printed to stdout.

#uncomment the following and add cross compiled iozone to this directory.
#mount -o remount,rw /
#iozone_cmd=$1"/iozone -a -i 0 -i 2 -s 16m -V teststring -b iozone_results"

#The original command with a -b so excel results are printed to stdout and can be parsed
iozone_cmd="iozone -a -i 0 -i 2 -s 16m -V teststring -b iozone_results"
echo execute command=${iozone_cmd}
${iozone_cmd}
echo IOZONE_RET_CODE=$?

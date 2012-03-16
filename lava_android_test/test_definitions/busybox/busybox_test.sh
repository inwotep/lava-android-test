#!/system/bin/sh

test_func(){
    if [ ! -f /system/bin/busybox ]; then
         echo "busybox=unexist"
         exit
    fi  

    if /system/bin/busybox [ $# -lt 1 ]; then
        return 0
    fi
    test_cmd=$1
    /system/bin/busybox "$@" 1>/dev/null 2>/dev/null
    if /system/bin/busybox [ $? -ne 0 ]; then
        echo "${test_cmd}=fail"
    else
        echo "${test_cmd}=pass"
    fi
}

rm -r /data/busybox 1>/dev/null 2>/dev/null

test_func mkdir /data/busybox
test_func touch /data/busybox/test.txt
test_func ls /data/busybox/test.txt
test_func ps
test_func whoami
test_func which busybox
test_func basename /data/busybox/test.txt
test_func cp /data/busybox/test.txt /data/busybox/test2.txt
test_func rm /data/busybox/test2.txt
test_func dmesg
test_func grep service /init.rc

rm -r /data/busybox 1>/dev/null 2>/dev/null

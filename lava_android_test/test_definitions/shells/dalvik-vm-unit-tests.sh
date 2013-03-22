#!/system/bin/sh
#
# Dalvik-VM unit tests.
#

chmod 777 /data/nativetest/dalvik-vm-unit-tests/dalvik-vm-unit-tests
/data/nativetest/dalvik-vm-unit-tests/dalvik-vm-unit-tests
if [ $? -eq 0 ]; then
	echo "dalvik-vm-unit-tests=pass"
else
	echo "dalvik-vm-unit-tests=fail"
fi

#!/system/bin/sh

echo "The custom shell will be run is:"
echo "    $@"
echo "Shell starts:"
$@
echo "Shell ends:"
RET=$?
echo "The exit status is: $RET"
if [ $? -ne 0 ]; then
    echo "custom=fail"
else
    echo "custom=pass"
fi

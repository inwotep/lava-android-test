#!/system/bin/sh

chmod 777 /data/nativebenchmark/binderAddInts
/data/nativebenchmark/binderAddInts "$@"
if [ $? -eq 0 ]; then
    echo "binder=PASS";
else
    echo "binder=FAIL";
fi

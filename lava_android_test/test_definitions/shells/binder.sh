#!/system/bin/sh

chmod 777 /data/nativebenchmark/binderAddInts
/data/nativebenchmark/binderAddInts "$@"
if [ $? -eq 0 ]; then
    echo "binder=pass";
else
    echo "binder=fail";
fi

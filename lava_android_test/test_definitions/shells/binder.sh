#!/system/bin/sh

chmod 777 /data/nativebenchmark/binderAddInts
if [ -z "$1" ]; then
	/data/nativebenchmark/binderAddInts -n 10
else
	/data/nativebenchmark/binderAddInts -n $1
fi
if [ $? -eq 0 ]; then
    echo "binder=pass";
else
    echo "binder=fail";
fi

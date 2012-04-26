#!/system/bin/sh

test_func(){
    if [ ! -f /system/bin/ime ]; then
         echo "ime=unexist"
         exit
    fi  

    /system/bin/ime list -a
    echo "ime=pass"
}

test_func

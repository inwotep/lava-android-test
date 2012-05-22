#!/system/bin/sh

test_func(){
    if [ ! -f /sys/class/android_usb/android0/state ]; then
         echo "usbhardware=fail"
         exit
    fi  

    cat /sys/class/android_usb/android0/state
    echo "usbhardware=pass"
}

test_func

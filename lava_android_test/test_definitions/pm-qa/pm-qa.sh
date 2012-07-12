#!/system/bin/sh

test_func(){
   if [ ! -d /system/xbin/pm-qa ]; then
       echo "pm-qa=fail"
       exit
   fi  

   mkdir /data/bin/
   cd /data/bin

   busybox ln -s -f /system/bin/busybox awk
   busybox ln -s -f /system/bin/busybox basename
   busybox ln -s -f /system/bin/busybox chmod
   busybox ln -s -f /system/bin/busybox chown
   busybox ln -s -f /system/bin/busybox cp
   busybox ln -s -f /system/bin/busybox diff
   busybox ln -s -f /system/bin/busybox find
   busybox ln -s -f /system/bin/busybox grep
   busybox ln -s -f /system/bin/busybox rm
   busybox ln -s -f /system/bin/busybox seq
   busybox ln -s -f /system/bin/busybox taskset
   busybox ln -s -f /system/bin/busybox tee
   busybox ln -s -f /system/bin/busybox printf
   busybox ln -s -f /system/bin/busybox wc

   busybox ln -s -f /system/bin/fake_command command
   busybox ln -s -f /system/bin/fake_sudo sudo
   busybox ln -s -f /system/bin/fake_udevadm udevadm

   export PATH=/data/bin:$PATH

   cd /system/xbin/pm-qa

   pwd=$PWD
   echo $pwd
   tests_dirs="cpuidle cpufreq cpuhotplug sched_mc suspend thermal utils"
   files=`find cpuidle cpufreq cpuhotplug sched_mc suspend -name "*.sh"`

   for dir in $tests_dirs
   do
       subDir=`pwd`/$dir
       if [ -d $subDir ]; then
       cd $subDir
       fi

       echo `pwd`
       for file in `find . -name "*.sh"`
       do
       path=$file
       echo $path
       /system/bin/sh $path
       done
       cd ..
   done

   echo "pm-qa=pass"
}

test_func

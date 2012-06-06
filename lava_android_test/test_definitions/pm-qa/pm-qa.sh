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
   busybox ln -s -f /system/bin/busybox tee
   busybox ln -s -f /system/bin/busybox printf
   busybox ln -s -f /system/bin/busybox wc

   export PATH=/data/bin:$PATH

   cd /system/xbin/pm-qa

   pwd=$PWD
   echo $pwd
   tests_dirs="cpuidle cpufreq cpuhotplug sched_mc suspend thermal utils"
   files=`find cpuidle cpufreq cpuhotplug sched_mc suspend thermal utils -name "*.sh"`

   for tests_dirs in $tests_dirs
   do
       subDir=`pwd`/$tests_dirs
       if [ -d $subDir ]; then
       cd $subDir
       fi

       echo `pwd`
       for dir in `find . -name "*.sh"`
       do
      path=$dir
      echo $path
      `echo $SHELL` $path
       done
       cd ..
   done

   echo "pm-qa=pass"
}

test_func

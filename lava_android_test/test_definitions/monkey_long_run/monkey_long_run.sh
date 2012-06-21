#!/system/bin/sh
#monkey_cmd="monkey -s 1 --pct-touch 10 --pct-motion 20 --pct-nav 20 --pct-majornav 30 --pct-appswitch 20 --throttle 500 2147483647"
if [ -e $1 ]; then
monkey_cmd="monkey -s 1 --pct-touch 10 --pct-motion 20 --pct-nav 20 --pct-majornav 30 --pct-appswitch 20 --throttle 500 --pkg-blacklist-file $1 25000"
else
monkey_cmd="monkey -s 1 --pct-touch 10 --pct-motion 20 --pct-nav 20 --pct-majornav 30 --pct-appswitch 20 --throttle 500 500"
echo "you did not have a blacklist file! so run the common way"
fi

echo execute command=${monkey_cmd}
${monkey_cmd}
echo MONKEY_RET_CODE=$?

#!/system/bin/sh
#monkey_cmd="monkey -s 1 --pct-touch 10 --pct-motion 20 --pct-nav 20 --pct-majornav 30 --pct-appswitch 20 --throttle 500 2147483647"
if [ $1 == 'juice' ]; then
monkey_cmd="monkey -s 1 --pct-touch 10 --pct-motion 20 --pct-nav 20 --pct-majornav 30 --pct-appswitch 20 --throttle 500 --pkg-blacklist-file $2 500"
else
monkey_cmd="monkey -s 1 --pct-touch 10 --pct-motion 20 --pct-nav 20 --pct-majornav 30 --pct-appswitch 20 --throttle 500 --pkg-blacklist-file $3 25000"
fi

echo execute command=${monkey_cmd}
${monkey_cmd}
echo MONKEY_RET_CODE=$?

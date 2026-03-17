#!/bin/bash

# -----------------------------------------------------------------------------
# https://www.cnblogs.com/jesn/p/17167544.html
# Check whether the network is open
function ping_domain() {
    # Domain name or DNS
    local domain=$1
    # Count of ping
    local tries=6
    # The count of successful requests
    local packets_responded=0

    for i in $(seq 1 $tries); do
        if ping -c 1 $domain >/dev/null; then
            packets_responded=`expr $packets_responded + 1`
            sleep 1
        fi
    done

    # If the total number of successful requests is greater than 2, it indicates success
    if [ $packets_responded -ge 2 ]; then
        echo "true"
    else
        echo "false"
    fi
}

# -----------------------------------------------------------------------------
if [ $(ping_domain www.baidu.com) = "false" ]; then echo "The network is unavailable, exit"; exit 1; fi
if [ $(ping_domain www.google.com) = "false" ]; then echo "Foreign network is unavailable, exit"; exit 1; fi

# https://unix.stackexchange.com/questions/463854/split-string-in-ash-shell-busybox
if ! test -f "./openclash_backup.sh"; then
    echo "\"./openclash_backup.sh\"" must exist.
    exit
fi

VERNESONG="https://raw.githubusercontent.com/vernesong/OpenClash"
packages=" \
    $VERNESONG/core/master/meta/clash-linux-amd64.tar.gz                       = clash_meta.tar.gz,\
    $VERNESONG/core/master/premium/clash-linux-amd64-2023.08.17-13-gdcc8d87.gz = clash_tun.gz,\
    $VERNESONG/core/master/dev/clash-linux-amd64.tar.gz                        = clash.tar.gz,\
    $VERNESONG/package/master/luci-app-openclash_0.45.157-beta_all.ipk         = openclash.ipk\
    "
OLDIFS=$IFS;IFS=,
for token in $packages; do
    url=$(echo ${token%=*})
    fname=$(echo ${token#*=})
    # https://unix.stackexchange.com/questions/102008/how-do-i-trim-leading-and-trailing-whitespace-from-each-line-of-some-output
    url=$(echo -e ${url} | sed 's/^[ \t]*//;s/[ \t]*$//')
    fname=$(echo -e ${fname} | sed 's/^[ \t]*//;s/[ \t]*$//')

    if ! test -f "./$fname"; then
        curl -v "$url" -o "./$fname" >/dev/null 2>&1
        res=$?
        if test "$res" != "0"; then
            echo "download $fname error, the curl command failed with: $res"
            if test -f "./$fname"; then
                rm -f "./$fname"
            fi
            exit 1
        fi
    fi
done
IFS=$OLDIFS

source ./openclash_backup.sh
if [ $? -ne 0 ]; then
    echo "Failed to execute script \"./openclash_backup.sh\"."
    exit 1
fi

res=$? && if test "$res" != "0"; then echo "backup openclash failed."; exit 1; fi

tar  -xzf "./clash_meta.tar.gz" -O > "./clash_meta"  &&  if ! test -f "./clash_meta"; then echo "uncompress \"./clash_meta.tar.gz\" failed."; exit 1; fi
tar  -xzf "./clash.tar.gz" -O      > "./clash"       &&  if ! test -f "./clash";      then echo "uncompress \"./clash.tar.gz\" failed.";      exit 1; fi
gzip -dkc "./clash_tun.gz"         > "./clash_tun"   &&  if ! test -f "./clash_tun";  then echo "uncompress \"./clash_tun.gz\" failed.";      exit 1; fi

opkg update && sleep 5

# https://github.com/vernesong/OpenClash/issues/1892
uci set openclash.config.enable='0'
uci commit openclash
/etc/init.d/openclash stop

openclash_watchdog_pids=$(ps |grep openclash_watchdog.sh |grep -v grep |awk '{print $1}' 2>/dev/null)
for watchdog_pid in $openclash_watchdog_pids; do
    kill -9 "$watchdog_pid" >/dev/null 2>&1
done

ocFolder="/etc/openclash"

# https://stackoverflow.com/questions/47560667/linux-kill-process-by-path
procPath="$ocFolder/clash" && kill $(pgrep -f "$procPath") >/dev/null 2>&1 && sleep 5 && if pgrep -f "$procPath" >/dev/null 2>&1; then echo "$procPath is running"; exit 1; fi

# https://forum.archive.openwrt.org/viewtopic.php?id=10824
procPathArr=" \
    $ocFolder/core/clash_meta \
    $ocFolder/core/clash \
    $ocFolder/core/clash_tun \
    "
for procPath in $procPathArr; do
    procPath=$(echo -e ${procPath} | sed 's/^[ \t]*//;s/[ \t]*$//')
    kill $(pgrep -f "$procPath") >/dev/null 2>&1 && if pgrep -f "$procPath" >/dev/null 2>&1; then echo "$procPath is running"; exit 1; fi
    # https://www.geeksforgeeks.org/basename-command-in-linux-with-examples/
    # https://stackoverflow.com/questions/7194192/basename-with-spaces-in-a-bash-script
    # https://stackoverflow.com/questions/3362920/get-just-the-filename-from-a-path-in-a-bash-script
    procName=$(basename ${procPath})
    mv -f "./$procName" "$procPath"
    chmod 755 "$procPath"
done

opkg --force-depends install "./openclash.ipk" >/dev/null 2>&1

if [ $? -ne 0 ]
then
    echo "opkg --force-depends install \"./openclash.ipk\" failed." >&2
    exit 1
fi

uci set openclash.config.enable='1'
uci commit openclash
/etc/init.d/openclash start
exit 0

# ------------------------------------- END -----------------------------------

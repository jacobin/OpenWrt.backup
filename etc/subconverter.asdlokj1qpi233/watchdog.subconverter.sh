#!/bin/bash

if ! test -f "/tmp/tmp/subconverter.crontab.flag.txt"; then
    exit 1
fi

# https://www.cnblogs.com/yuyanc/p/16434413.html
step=5
for (( i = 0; i < 60; i=(i+step) )); do

    # https://stackoverflow.com/questions/9117507/linux-unix-command-to-determine-if-process-is-running
    PROCESS=/etc/subconverter.asdlokj1qpi233/subconverter
    PIDS=`ps | grep -v grep | grep -v watchdog | grep $PROCESS | grep -o '^[ ]*[0-9]*'`
    if [ -z "$PIDS" ]; then
        echo fuckup ...
        /etc/init.d/subconverter.asdlokj1qpi233 start
    else
        for PID in $PIDS; do
            echo $PID
        done
    fi

    sleep $step
done

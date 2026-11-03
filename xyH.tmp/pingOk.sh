#!/bin/bash

function checkIP() {
    ip=$1
    ((count = 3))                           # Maximum number to try.
    while [[ $count -ne 0 ]] ; do
        ping -c 1 $ip  &>/dev/null          # Try once.
        rc=$?
        if [[ $rc -eq 0 ]] ; then
            ((count = 1))                   # If okay, flag loop exit.
        else
            sleep 1                         # Minimise network storm.
        fi
        ((count = count - 1))               # So we don't go forever.
    done

    if [[ $rc -eq 0 ]] ; then               # Make final determination.
        return 0
    else
        return 1
    fi
}

if checkIP "8.8.8.8"; then
    echo "8.8.8.8" is ok.
else
    echo "8.8.8.8" is bad.
fi

if checkIP "114.114.114.114"; then
    echo "114.114.114.114" is ok.
else
    echo "114.114.114.114" is bad.
fi

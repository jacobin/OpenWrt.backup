#!/bin/bash

###############################################################################
######################### function: is_valid_date #############################
###############################################################################
function is_valid_date() {
    # OpenWrt uses the busybox-date utility to manage time, supporting formats
    # like YYYY-MM-DD hh:mm[:ss], [YYYY.]MM.DD-hh:mm[:ss],
    # or [[[[[YY]YY]MM]DD]hh]mm[.ss]. The command date -s is used to manually
    # set the system time, while ntpd -q -p is used for syncing via NTP.
    date -D "%Y%m%d_%H%M%S" "$1" > NUL 2>&1
    if [ $? -eq 0 ]; then
        return 0
    fi

    return 1
}

###############################################################################
######################### function: is_valid_date #############################
###############################################################################
function is_valid_date2() {
    date_arg="$1"
    # Regex for YYYY-MM-DD format
    if [[ "$date_arg" =~ ^[0-9]{4}[0-9]{2}[0-9]{2}_[0-9]{2}[0-9]{2}[0-9]{2}$ ]]; then
        return 0
    fi
    return 1
}

###############################################################################
######################### function: is_valid_date #############################
###############################################################################
# https://stackoverflow.com/questions/10759162/check-if-argument-is-a-valid-date-in-bash-shell
function is_valid_date3() {
    DATE="$1"
    Y=${DATE:0:4}
    m=${DATE:4:2}
    d=${DATE:6:2}
    if date -d "$Y-$m-$d" &> /dev/null; then
        return 0
    fi
    return 1
}

# Example Usage:
function Testcase() {
    if is_valid_date3 "$1"; then
        echo "'$1' is a valid date."
    else
        echo "'$1' is not a valid date."
    fi
}

Testcase "20220228_120342"
Testcase "20220231_120342"
Testcase "20220238_120342"

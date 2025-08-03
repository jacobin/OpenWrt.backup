#!/bin/sh
get_vars() {
    echo "value1 value2"
}

main() {
    local vars="$(get_vars)"
    local var1="$(echo ${vars} | awk '{print $1}')"
    local var2="$(echo ${vars} | awk '{print $2}')"

    echo "var1='$var1', var2='$var2'"
}

main
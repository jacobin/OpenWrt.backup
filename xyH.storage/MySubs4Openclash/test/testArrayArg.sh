#!/bin/bash

generatearray() {
    # $1 is array name in which array is generated
    local -n array="$1" || return 1
    array=( foo doo coo )
}
# call function that constructs the array with the array name
generatearray targetvalue
# display it
declare -p targetvalue
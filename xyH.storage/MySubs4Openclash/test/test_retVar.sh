#!/bin/bash
#
#function aFunc() {
#    retVar=$1
#    echo ${retVar}
#    eval "${1}='fuck you'"
#}
#
#retVV="fuck she"
#aFunc retVV
#echo ${retVV}

#--------------------------------- fnDigString --------------------------------
# # https://stackoverflow.com/questions/16623835/remove-a-fixed-prefix-suffix-from-a-string-in-bash
function fnDigString() { # $1/return var, $2/originalString, $3/prefix, $4/suffix
    local originalString="$2"
    local prefix="$3"
    local suffix="$4"
    local foo=${originalString#"$prefix"}
    foo=${foo%"$suffix"}
    eval "${1}='${foo}'"
}
 # Example:
     ret=33333333333333333333333333333
     fnDigString "ret" "1234567890" "12" "890"
     echo $ret
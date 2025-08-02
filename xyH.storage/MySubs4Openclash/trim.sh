#!/bin/bash

###############################################################################
#--------------------------------- trim ---------------------------------------
# https://blog.longwin.com.tw/2018/02/bash-shell-sed-trim-function-2018/
function trim() {
    if [ -z $1 ]; then # $1 is unset
        sed -e 's/^ *//' -e 's/ *$//'
    else
        # echo "=== $1 ==="
        sed -e 's/^ *//' -e 's/ *$//' -e "s/^$1//" -e "s/$1$//"
    fi
}
# # Example:
#     echo "=== aaaaaaaaaaaaaaaaaa ===" | trim '=' | trim '=' | trim '='
#     echo " [aaaaaaaaaaaaaaaaaa]" | trim ' ' | trim "\[" | trim "\]"

#--------------------------------- End ----------------------------------------

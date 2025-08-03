#!/bin/sh
# function return_multiple_values() {
#     eval "$1='What is your name'"
#     eval "$2='my name is: BASH'"
# }
#     
# return_var=''
# res2=''
# return_multiple_values return_var res2
# echo $return_var
# echo $res2

function return_multiple_values() {
    url=www.china.com
    outFilename=./aaa.txt
    eval "$1=$url"
    eval "$2=$outFilename"
}
    
return_var=''
res2=''
return_multiple_values return_var res2
echo $return_var
echo $res2
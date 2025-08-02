#!/bin/sh

foo=""
bar=""

function my_func(){
    aaa=$1
    bbb=$2
    echo 'foo="$aaa"; bar="$bbb"'
}

eval $(my_func "a" "b" )
echo $foo $bar
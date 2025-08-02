#!/bin/sh

foo=""
bar=""

my_func(){
    echo 'foo="$1"; bar="$2"'
}

eval $(my_func a b )
echo $foo $bar
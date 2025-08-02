#!/bin/bash

#https://blog.csdn.net/guoqx/article/details/135889940


function funcLevel2() {
    local b=100
    echo $FUNCNAME -- $a
}

function funcLevel1() {
    local a=99
    funcLevel2
}

a=123
funcLevel1
echo funcLevel0 -- $a
#!/bin/bash

function aFunc() {
    subs="a\|b\|c"
    eval "$1=$subs"
}

function Main() {
    aFunc VAL
    echo $VAL
}

Main
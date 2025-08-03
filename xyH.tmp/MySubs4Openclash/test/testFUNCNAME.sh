#!/bin/bash

# https://stackoverflow.com/questions/1835943/how-to-determine-function-name-from-inside-a-function
# in a file "foobar"
function foo {
    echo foo
    echo "In function $FUNCNAME: FUNCNAME=${FUNCNAME[*]}" >&2
}

function foobar {
    echo "$(foo)bar"
    echo "In function $FUNCNAME: FUNCNAME=${FUNCNAME[*]}" >&2
}

foobar
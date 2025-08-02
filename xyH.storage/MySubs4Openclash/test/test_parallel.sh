#!/bin/bash

function aFunc() {
    echo "${1}--${SSS}"
    SSS="$1""$SSS"
    echo $SCRIPT_DIR
}

function Main() {
    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

    SSS="AAAAAA"
    for i in {1..20};do
        aFunc $i &
    done
    echo "END"
}

Main
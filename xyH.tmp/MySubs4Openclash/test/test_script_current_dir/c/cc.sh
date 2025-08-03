#!/bin/bash
# SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# SCRIPT_DIR=$(dirname "$0")
# echo $SCRIPT_DIR

echo "--Usage: $(basename $BASH_SOURCE) ..."

function aFunc() {
    echo "--Usage: $(basename $BASH_SOURCE) ..."
    echo "--$FUNCNAME"
}

aFunc
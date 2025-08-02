#!/bin/bash

###############################################################################
function fnExtractStringBetweenAB() {  # $1/return var, $2/originalString, $3/A string, $4/B string
  # echo $2
  # echo $3
  # echo $4
    local foo="$2"
    foo=${foo##*${3}}
    foo=${foo%%${4}*}
  # echo [$foo]
  # echo "${1}='${foo}'"
    eval "${1}='${foo}'"
}
## Example:
    fnExtractStringBetweenAB ret '{"name":"2025-03","path":"node-list/2025-03","contentType":"directory"}],"templateDirectorySuggestionUrl":null,"readme":null,"totalCount":26,"showBranchInfobar":false},"fileTree":{"":{"items":[' \
        '"path":"node-list/' \
        '","contentType":"directory"'

    echo [${ret}]
    ret=`echo $ret | xargs`
    echo [${ret}]

#!/bin/bash

# IN="111111&222222222222&33333333333&444444444&a href="
# IFS='&' read -ra ADDR <<< "$IN"
# for i in "${ADDR[@]}"; do
#    echo $i
# done

function GenGrepLineFilter() {
    filterKeyword="$2"
    greps=
    IFS='&' read -ra ADDR <<< "${filterKeyword}"
    for G in "${ADDR[@]}"; do
        greps="${greps} | grep  \\\"${G}\\\" "
    done

    eval "${1}=$(echo \"${greps}\")"
}

GenGrepLineFilter ret "5月25日&最高速度&最新高速&订阅链接免费节点&a href="

eval "cat \"gggg.html\" ${ret}"

#
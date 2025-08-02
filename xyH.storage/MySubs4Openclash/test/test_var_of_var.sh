#!/bin/bash

#https://stackoverflow.com/questions/10757380/bash-variable-variables
  # arrayName="array${RANDOM}${RANDOM}"
  # eval "${arrayName}=11111111111"
  # echo ${arrayName}
  # echo "${!arrayName}"

  # refUrl="https://nodefree.org, [5月25日&最高速度&最新高速&订阅链接免费节点&a href=#a href=#title=], [https://nodefree.org/dy/&.txt#<p>#</p>]"
  # ## https://stackoverflow.com/questions/10586153/how-to-split-a-string-into-an-array-in-bash
  # IFS=',' read -r -a "arrayName" <<< "${refUrl}"
  # for element in "${arrayName[@]}"
  # do
  #     echo "$element"++++
  # done


###############################################################################
#--------------------------------- trim ---------------------------------------
# https://blog.longwin.com.tw/2018/02/bash-shell-sed-trim-function-2018/
function trim() {
    if [ -z $1 ]; then # $1 is unset
        sed -e 's/^ *//' -e 's/ *$//'
    else
        # echo "=== $1 ==="
        sed -e 's/^ *//' -e 's/ *$//' -e "s/^$1//" -e "s/$1$//"
    fi
}
# # Example:
#     echo "=== aaaaaaaaaaaaaaaaaa ===" | trim '=' | trim '=' | trim '='
#     echo " [aaaaaaaaaaaaaaaaaa]" | trim ' ' | trim "\[" | trim "\]"


###############################################################################
#--------------------------------- fnExtractIntermediateUrl -------------------
function fnExtractIntermediateUrl() {
          outUrl=${1}
    local entryURL=${2}       # https://nodefree.org
    local filter=${3}         #[5月25日&最高速度&最新高速&订阅链接免费节点&a href=#a href=#title=]
    local name=${4}
    local threadDatetime=${5}

    filter=$( echo "${filter}" | trim ' ' | trim '\[' | trim '\]' | trim ' ' )

    local arrayName="array${RANDOM}${RANDOM}"
    IFS='#' read -r -a "${arrayName}" <<< "${filter}"
    local count=$( eval echo "\${#${arrayName}[@]}" )
    if [ "$count" -ne 3 ]; then
        echo "The definition file format is incorrect:\"$filter\"" | tee "${TMP_FOLDER}/${name}-${threadDatetime}.log"
        exit 1
    fi

    local filterKeyword=$( eval echo "\${${arrayName}[0]}" )
    local digPrefix=$( eval echo "\${${arrayName}[1]}" )
    local digsuFfix=$( eval echo "\${${arrayName}[2]}" )

  # eval echo "\${outUrl}"
  # echo $filterKeyword
  # echo $digPrefix
  # echo $digsuFfix
    source ../download_and_extract_link.sh "-u${entryURL}" "-s${outUrl}" "-t${threadDatetime}" "-k${filterKeyword}" "-p${digPrefix}" "-f${digsuFfix}"
}

###############################################################################
    export "TMP_FOLDER=/xyH.storage/MySubs4Openclash/tmp"
    threadDatetime=$(date "+%Y-%m-%d_%H-%M-%S")"-${RANDOM}-${RANDOM}"
    name=xfxssr

    refUrl="https://nodefree.org, [5月25日&最高速度&最新高速&订阅链接免费节点&a href=#a href=#title=], [https://nodefree.org/dy/&.txt#<p>#</p>]"
    arrayName="array${RANDOM}${RANDOM}"
    ## https://stackoverflow.com/questions/10586153/how-to-split-a-string-into-an-array-in-bash
    ## https://www.coder.work/article/2567613
    IFS=',' read -r -a "${arrayName}" <<< "${refUrl}"

  # echo "\${#${arrayName}[@]}"
  ## ${#array2874311001[@]}
    count=$( eval echo "\${#${arrayName}[@]}" )
  # echo $count

  # echo "\${${arrayName}[1]}"
  ## ${array2874311001[1]}
    finalUrl=$( eval echo "\${${arrayName}[0]}" )

    if [ "${count}" -gt 1 ]; then
      # array="${arrayName}[@]"
      # for element in "${!array}"
      # do
      #     echo "$element"
      # done
        for ((i=1; i<${count}; i++));
        do
            thisFilter=$( eval echo "\${${arrayName}[${i}]}" )
            fnExtractIntermediateUrl "finalUrl" "${finalUrl}" "${thisFilter}" "${name}" "${threadDatetime}"
        done
    fi

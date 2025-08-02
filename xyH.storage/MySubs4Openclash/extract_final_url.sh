#!/bin/bash

###############################################################################
function fnExtractIntermediateUrl() {
    local usage="Usage: $FUNCNAME <-sOutSuburl> <-uEntryUrl> <-lFiLter> <-nName> <-h>"
    ## https://stackoverflow.com/questions/5048326/getopts-wont-call-twice-in-a-row
    local OPTIND
    local flag=

    local outSuburl=
    local entryUrl=       # https://nodefree.org
    local fiLter=         # [5月25日&最高速度&最新高速&订阅链接免费节点&a href=#a href=#title=]
    local name=

    ## https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script
    while getopts ":s:u:l:n:h" flag
    do
        case "${flag}" in
            s) outSuburl=${OPTARG};;
            u) entryUrl=${OPTARG};;
            l) fiLter=${OPTARG};;
            n) name=${OPTARG};;
            h) printf "${usage}\n" >"$out" 2>"$err"
               exit
               ;;
            :) printf "missing argument for -%s\n" "${OPTARG}" >"$out" 2>"$err"
               printf "${usage}\n" >"$out" 2>"$err"
               exit 1
               ;;
           \?) printf "illegal option: -%s\n" "${OPTARG}" >"$out" 2>"$err"
               printf "${usage}\n" >"$out" 2>"$err"
               exit 1
               ;;
            *) printf "${usage}\n" >"$out" 2>"$err"
               exit 1
               ;;
        esac
    done
    shift $(( OPTIND - 1 ))

    source "${SCRIPT_ROOT_DIR}/trim.sh"
    fiLter=$( echo "${fiLter}" | trim ' ' | trim '\[' | trim '\]' | trim ' ' )

    local arrayName="array${RANDOM}${RANDOM}"
    IFS='#' read -r -a "${arrayName}" <<< "${fiLter}"
    local count=$( eval echo "\${#${arrayName}[@]}" )
    if [ "${count}" -ne 3 ]; then
        echo "The definition file format is incorrect:\"$fiLter\"" >"$out" 2>"$err"
        return 1
    fi

    local fiLterKeyword=$( eval echo "\${${arrayName}[0]}" )
    local digPrefix=$( eval echo "\${${arrayName}[1]}" )
    local digsuFfix=$( eval echo "\${${arrayName}[2]}" )

#   echo ${outSuburl}
#   eval echo "\${${outSuburl}}"
#   echo  ${entryUrl}
#   echo  ${fiLterKeyword}
#   echo  ${digPrefix}
#   echo  ${digsuFfix}
#   exit 1
    source "${SCRIPT_ROOT_DIR}/download_and_extract_url.sh" "-u${entryUrl}" "-s${outSuburl}" "-k${fiLterKeyword}" "-p${digPrefix}" "-f${digsuFfix}"
    if [ $? -ne 0 ]; then
        return 1
    fi
}

###############################################################################
function fnExtractFinalUrl() {
    local usage="Usage: $FUNCNAME <-uRefUrl> <-fOutFinalUrl> <-h>"

    ## https://stackoverflow.com/questions/5048326/getopts-wont-call-twice-in-a-row
    local OPTIND
    local flag=
    local refUrl=
    local outFinalUrl=

    ## https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script
    while getopts ":u:f:h" flag
    do
        case "${flag}" in
            u) refUrl=${OPTARG};;
            f) outFinalUrl=${OPTARG};;
            h) printf "${usage}\n" >"$out" 2>"$err"
               exit
               ;;
            :) printf "missing argument for -%s\n" "${OPTARG}" >"$out" 2>"$err"
               printf "${usage}\n" >"$out" 2>"$err"
               exit 1
               ;;
           \?) printf "illegal option: -%s\n" "${OPTARG}" >"$out" 2>"$err"
               printf "${usage}\n" >"$out" 2>"$err"
               exit 1
               ;;
            *) printf "${usage}\n" >"$out" 2>"$err"
               exit 1
               ;;
        esac
    done
    shift $(( OPTIND - 1 ))

    if [ -z "${refUrl}" ] || [ -z "${outFinalUrl}" ]; then
        printf "${usage}\n" >"$out" 2>"$err"
        exit 1
    fi

    local arrayName="array${RANDOM}${RANDOM}"
    ## https://stackoverflow.com/questions/10586153/how-to-split-a-string-into-an-array-in-bash
    ## https://www.coder.work/article/2567613
    IFS=',' read -r -a "${arrayName}" <<< "${refUrl}"

  # echo "\${#${arrayName}[@]}"
  ## ${#array2874311001[@]}
    local count=$( eval echo "\${#${arrayName}[@]}" )
  # echo $count

  # echo "\${${arrayName}[1]}"
  ## ${array2874311001[1]}
    local finalUrl=$( eval echo "\${${arrayName}[0]}" )

    if [ "${count}" -gt 1 ]; then
      # array="${arrayName}[@]"
      # for element in "${!array}"
      # do
      #     echo "$element"
      # done
        for ((i=1; i<${count}; i++));
        do
            local thisFilter=$( eval echo "\${${arrayName}[${i}]}" )
            fnExtractIntermediateUrl "-sfinalUrl" "-u${finalUrl}" "-l${thisFilter}" "-n${name}"
            if [ $? -ne 0 ]; then
                eval "${outFinalUrl}="
                return 1
            fi
        done
    fi
    eval "${outFinalUrl}=${finalUrl}"
}

###############################################################################
# https://stackoverflow.com/questions/1878882/how-do-i-create-an-array-in-unix-shell-scripting
#   Unquoted, $@ is the same as $*; the difference only shows up when quoted: "$*" is one word, while "$@" preserves the original word breaks.
fnExtractFinalUrl "$@"
## Example:
#    TMP_FOLDER="/xyH.storage/MySubs4Openclash/tmp"
#    SCRIPT_ROOT_DIR="/xyH.storage/MySubs4Openclash"
#    name="xfxssr"
#
#    threadDatetime=$(date "+%Y-%m-%d_%H-%M-%S")"-${RANDOM}-${RANDOM}-$$"
#
#    # https://stackoverflow.com/questions/692000/how-do-i-write-standard-error-to-a-file-while-using-tee-with-a-pipe/692407#692407
#    # https://unix.stackexchange.com/questions/352107/generic-way-to-get-temp-path
#    out="${TMP_FOLDER:-/tmp}/out.$$" err="${TMP_FOLDER:-/tmp}/err.$$"
#    mkfifo "$out" "$err"
#    trap 'rm "$out" "$err"' EXIT
#    tee -a "${SCRIPT_ROOT_DIR}/log/${name}.${threadDatetime}.stdout.log" < "$out" &
#    tee -a "${SCRIPT_ROOT_DIR}/log/${name}.${threadDatetime}.stderr.log" < "$err" >&2 &
#
#    fnExtractFinalUrl "-uhttps://nodefree.org, [月&日&最高速度&最新高速&订阅链接免费节点&a href=#a href=#title=], [https://nodefree.org/dy/&.txt#<p>#</p>]" "-foutFinalUrl2"
#    if [ $? -ne 0 ]; then
#        echo "fnExtractFinalUrl failed."
#        return 1
#    fi
#
#    echo ${outFinalUrl2}

################################## End ########################################

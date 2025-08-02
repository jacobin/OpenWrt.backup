#!/bin/bash




###############################################################################
function fnGenGrepLineFilter() { # $1/return var, $2/filterKeywordList -- 譬如『5月25日&最高速度&最新高速&订阅链接免费节点&a class=&item-img-inner& href=』，其中不能有双引号
    local filterKeyword="$2"
    local greps=
    IFS='&' read -ra ADDR <<< "${filterKeyword}"
    for G in "${ADDR[@]}"; do
        greps="${greps} | grep  \\\"${G}\\\" "
    done

    eval "${1}=$(echo \"${greps}\")"
}
## Example:
## https://nodefree.org/
#    fnGenGrepLineFilter ret "5月25日&最高速度&最新高速&订阅链接免费节点&a class=&item-img-inner& href="
#    eval "cat \"gggg.html\" ${ret}"





###############################################################################
# # https://stackoverflow.com/questions/16623835/remove-a-fixed-prefix-suffix-from-a-string-in-bash
function fnDigString() { # $1/return var, $2/originalString, $3/prefix, $4/suffix
    local originalString="$2"
    local prefix="$3"
    local suffix="$4"
    local foo=${originalString#"$prefix"}
    foo=${foo%"$suffix"}
    eval "${1}=${foo}"
}
## Example:
#    fnDigString "ret" "1234567890" "12" "890"
#    echo $ret





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
#    fnExtractStringBetweenAB ret "<p class=\"item-title\"><a href=\"https://nodefree.org/p/2067.html\" title=\"「5月25日」最高速度13.56M/S，2024年最新高速SSR/V2ray/Clash订阅链接免费节点\">「5月25日」最高速度13.56M/S，2024年最新高速SSR/V2ray/Clash订阅链接免费节点</a></p>" \
#        "a href=" \
#        "title="
#
#    echo [${ret}]
#    ret=`echo $ret | xargs`
#    echo [${ret}]





###############################################################################
function fnDownloadAndExtractUrl() {
    local usage="Usage: $FUNCNAME <-uRefUrl> <-sOutSuburl> <-h> <-kFilterKeyword> <-pDigPrefix> <-fDigsuFfix>"

    ## https://stackoverflow.com/questions/5048326/getopts-wont-call-twice-in-a-row
    local OPTIND
    local flag=
    local refUrl=
    local outSuburl=
    local filterKeyword=
    local digPrefix=
    local digsuFfix=

    ## https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script
    while getopts ":u:s:hk:p:f:" flag
    do
        case "${flag}" in
            u) refUrl=${OPTARG};;
            s) outSuburl=${OPTARG};;
            h) printf "${usage}\n" >"$out" 2>"$err"
               exit
               ;;
            k) filterKeyword=${OPTARG};;
            p) digPrefix=${OPTARG};;
            f) digsuFfix=${OPTARG};;
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

  # echo "${refUrl}"
  # echo "${outSuburl}"
  # echo "${filterKeyword}"
  # echo "${digPrefix}"
  # echo "${digsuFfix}"
  # exit 1

    if [ -z "${refUrl}" ] || [ -z "${outSuburl}" ] || [ -z "${filterKeyword}" ] || [ -z "${digPrefix}" ] || [ -z "${digsuFfix}" ]; then
        printf "${usage}\n" >"$out" 2>"$err"
        exit 1
    fi

    if [ -z "${TMP_FOLDER}" ]; then
        printf "Environment variables \"TMP_FOLDER\" is empty.\n" >"$out" 2>"$err"
        exit 1
    fi

  # ## https://stackoverflow.com/questions/192319/how-do-i-know-the-script-file-name-in-a-bash-script
  # ## https://stackoverflow.com/questions/965053/extract-filename-and-extension-in-bash
  # local fileNameExt=$(basename $BASH_SOURCE)
  # local name="${fileNameExt%.*}"
    local tmpRefWebpageFPath="${TMP_FOLDER}/PID$$-${RANDOM}-ReferringWebPages.html"

    wget "${refUrl}" -O${tmpRefWebpageFPath}
    if [ $? -ne 0 ]; then
        printf "%s, download \"%s\" failed.\n" "$FUNCNAME" "${refUrl}" >"$out" 2>"$err"
        eval "${outSuburl}="
        return 1
    fi

    local retFilterKeyword=
    fnGenGrepLineFilter retFilterKeyword "${filterKeyword}"
    ## https://stackoverflow.com/questions/6114119/how-do-i-read-the-first-line-of-a-file-using-cat
    local aLine=$(eval "cat \"${tmpRefWebpageFPath}\" ${retFilterKeyword} | sed -n 1p")
    if [ -z "${aLine}" ]; then
        printf "%s, there is no the specified URL in the file \"%s\"\n" "$FUNCNAME" "${tmpRefWebpageFPath}" >"$out" 2>"$err"
        eval "${outSuburl}="
        return 1
    fi

    rm -f "${tmpRefWebpageFPath}"

    local digedLink=
    fnExtractStringBetweenAB digedLink "${aLine}" "${digPrefix}" "${digsuFfix}"
    if [ -z "${digedLink}" ]; then
        printf "%s, there is no the specified URL in the line \"%s\"\n" "$FUNCNAME" "${aLine}" >"$out" 2>"$err"
        eval "${outSuburl}="
        return 1
    fi

    eval "${outSuburl}=${digedLink}"
}





###############################################################################
# https://stackoverflow.com/questions/1878882/how-do-i-create-an-array-in-unix-shell-scripting
#   Unquoted, $@ is the same as $*; the difference only shows up when quoted: "$*" is one word, while "$@" preserves the original word breaks.
fnDownloadAndExtractUrl "$@"
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
#    tee -a "${SCRIPT_ROOT_DIR}/${name}.${threadDatetime}.stdout.log" < "$out" &
#    tee -a "${SCRIPT_ROOT_DIR}/${name}.${threadDatetime}.stderr.log" < "$err" >&2 &
#
#    fnDownloadAndExtractUrl "-uhttps://nodefree.org" -sOutSuburl "-k月&日&最高速度&最新高速&订阅链接免费节点&a class=&item-img-inner& href=" "-p href=" "-ftitle="
#    if [ $? -ne 0 ]; then
#        echo "fnDownloadAndExtractUrl failed."
#        return 1
#    fi
#
#    echo ${OutSuburl}





################################## End ########################################

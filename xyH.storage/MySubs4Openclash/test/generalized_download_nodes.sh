#!/bin/bash

#--------------------------------- fnGeneralizedDownloadNodes -----------------
function fnGeneralizedDownloadNodes() {
    local usage="Usage: $(basename $BASH_SOURCE) <-cSubConverter> <-uSubUrl> <-nName> <-tThreadDatetime> <-h>"

    # https://stackoverflow.com/questions/5048326/getopts-wont-call-twice-in-a-row
    local OPTIND
    local flag
    local subConverter
    local subUrl
    local name
    local threadDatetime

    # https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script
    # https://stackoverflow.com/questions/16483119/an-example-of-how-to-use-getopts-in-bash
    # https://stackoverflow.com/questions/5474732/how-can-i-add-a-help-method-to-a-shell-script
    while getopts ":c:u:n:t:h" flag
    do
        case "${flag}" in
            c) subConverter=${OPTARG};;
            u) subUrl=${OPTARG};;
            n) name=${OPTARG};;
            t) threadDatetime=${OPTARG};;
            h) printf "${usage}\n"
               exit
               ;;
            :) printf "missing argument for -%s\n" "${OPTARG}" >&2
               printf "${usage}\n" >&2
               exit 1
               ;;
           \?) printf "illegal option: -%s\n" "${OPTARG}" >&2
               printf "${usage}\n" >&2
               exit 1
               ;;
            *) printf "${usage}\n" >&2
               exit 1
               ;;
        esac
    done
    shift $(( OPTIND - 1 ))

    if [ -z "${subConverter}" ] || [ -z "${subUrl}" ] || [ -z "${name}" ] || [ -z "${threadDatetime}" ]; then
        printf "${usage}\n" >&2
        exit 1
    fi

    ## include <fnUrlEncode.sh>
    source "${SCRIPT_ROOT_DIR}/url_encode.sh"
    local base64Suburl=`fnUrlEncode "${subUrl}"`

    fILTER="function%20filter%28node%29%20%7B%0A%20%20%20%20if%28node.Type."`
          `"toLowerCase%28%29%20%3D%3D%3D%20%22ss%22%20%26%26%20node.Encryp"`
          `"tMethod.toLowerCase%28%29%20%3D%3D%3D%20%22chacha20-poly1305%22"`
          `"%29%20%7B%0A%20%20%20%20%20%20%20%20return%20false%3B%0A%20%20%"`
          `"20%20%7D%0A%20%20%20%20return%20true%3B%0A%7D"
    eXCLUDE="%28%E4%B8%AD%E5%9C%8B%7C%E9%A6%99%E6%B8%AF%7C%E4%B8%AD%E5%9B%B"`
           `"D%7CCN%7CHK%7CHong%20Kong%7CHongKong%7C%E5%B9%BF%E4%B8%9C%7C%E"`
           `"8%B4%B5%E5%B7%9E%7C%E5%8C%97%E4%BA%AC%7C%E4%B8%8A%E6%B5%B7%7C%"`
           `"E7%A7%BB%E5%8A%A8%7Cv2cross%29"
    ## https://stackoverflow.com/questions/7729023/how-do-i-break-up-an-extremely-long-string-literal-in-bash
    local urlPrefix="${subConverter}/sub?target=clash"`
                                      `"&config=ACL4SSR_Online_Full_AdblockPlus.ini"`
                                      `"&enable_filter=true"`
                                      `"&filter_script=${fILTER}"`
                                      `"&exclude=${eXCLUDE}"`
                                      `"&append_type=true"`
                                      `"&emoji=true"`
                                      `"&list=false"`
                                      `"&udp=true"`
                                      `"&tfo=true"`
                                      `"&scv=true"`
                                      `"&fdn=true"
    local finalSuburl="${urlPrefix}&url=${base64Suburl}"

    local tmpYaml="${TMP_FOLDER}/${name}-${threadDatetime}.yml"
    wget "${finalSuburl}" -O"${tmpYaml}"
    if [ $? -ne 0 ]
    then
        echo "Download \"${finalSuburl}\" fail." | tee "${TMP_FOLDER}/${name}-${threadDatetime}.log"
        exit 1
    fi

    # https://stackoverflow.com/questions/9964823/how-to-check-if-a-file-is-empty-in-bash
    if [[ -z $(grep '[^[:space:]]' "${tmpYaml}") ]] ; then
        echo "No nodes are downloaded" | tee "${TMP_FOLDER}/${name}-${threadDatetime}.log"
        exit 1
    fi

    local targetYaml="${TARGET_YAML_FOLDER}/${name}.yml"
    rm -f "${targetYaml}"
    mv -f "${tmpYaml}" "${targetYaml}"
}

###############################################################################
# https://stackoverflow.com/questions/1878882/how-do-i-create-an-array-in-unix-shell-scripting
#   Unquoted, $@ is the same as $*; the difference only shows up when quoted: "$*" is one word, while "$@" preserves the original word breaks.
fnGeneralizedDownloadNodes "$@"

#--------------------------------- End ----------------------------------------

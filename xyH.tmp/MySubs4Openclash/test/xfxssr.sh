#!/bin/bash

#--------------------------------- fnExtractSubsCallback ----------------------
function fnExtractSubsCallback() {
    local usage="Usage: $(basename $BASH_SOURCE) <-uRefUrl> <-sOutSuburls> <-tThreadDatetime> <-h> -gGrepKeyword"

    ## https://stackoverflow.com/questions/5048326/getopts-wont-call-twice-in-a-row
    local OPTIND
    local flag
    local refUrl
   #local outSuburls
    local threadDatetime
    local grepKeyword
    local flag

    ## https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script
    while getopts ":u:s:t:hg:" flag
    do
        case "${flag}" in
            u) refUrl=${OPTARG};;
            s) outSuburls=${OPTARG};;
            t) threadDatetime=${OPTARG};;
            h) printf "${usage}"
               exit
               ;;
            g) grepKeyword=${OPTARG};;
            :) printf "missing argument for -%s\n" "${OPTARG}" >&2
               printf "${usage}" >&2
               exit 1
               ;;
           \?) printf "illegal option: -%s\n" "${OPTARG}" >&2
               printf "${usage}" >&2
               exit 1
               ;;
            *) printf "${usage}" >&2
               exit 1
               ;;
        esac
    done
    shift $(( OPTIND - 1 ))

    if [ -z "${refUrl}" ] || [ -z "${outSuburls}" ] || [ -z "${threadDatetime}" ]; then
        printf "${usage}" >&2
        exit 1
    fi

    ## https://stackoverflow.com/questions/192319/how-do-i-know-the-script-file-name-in-a-bash-script
    ## https://stackoverflow.com/questions/965053/extract-filename-and-extension-in-bash
    local fileNameExt=$(basename $BASH_SOURCE)
    local name="${fileNameExt%.*}"
    local tmpRefUrl="${TMP_FOLDER}/${name}-${threadDatetime}-ReferringWebPages.html"

    wget "${refUrl}" -O${tmpRefUrl}
    if [ $? -ne 0 ]; then
        echo "download ${tmpRefUrl} failed." | tee "${TMP_FOLDER}/${name}-${threadDatetime}.log"
        exit 1
    fi

    local tmpOnlysubs="${TMP_FOLDER}/${name}-${threadDatetime}-ExtractSubs.txt"
    # cat "${tmpRefUrl}" | grep "https://www.xfxssr.com/api/v1/client/subscribe" > "${tmpOnlysubs}"
    cat "${tmpRefUrl}" | grep "${grepKeyword}" > "${tmpOnlysubs}"
    rm -f "${tmpRefUrl}"
    if [[ -z $(grep '[^[:space:]]' "${tmpOnlysubs}") ]] ; then
        echo "There is no subscription link in the file \"${tmpOnlysubs}\"" | tee "${TMP_FOLDER}/${name}-${threadDatetime}.log"
        exit 1
    fi

    local L=
    local subs=
    while read L; do
        if [ -z "${subs}" ]
        then
            subs="${L}"
        else
            subs="${subs}\|${L}"
        fi
    done < "${tmpOnlysubs}"

    rm -f "${tmpOnlysubs}"

    eval ${outSuburls}=${subs}
}

fnExtractSubsCallback $@

#--------------------------------- End ----------------------------------------

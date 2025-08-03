#!/bin/bash

source ../trim.sh
function afunc() {
    local TARGET_DOWNLOAD_FOLDER="/xyH.storage/MySubs4Openclash/download"
    local Urls=

    local FILES="${TARGET_DOWNLOAD_FOLDER}/*"
    for f in $FILES
    do
        Urls=$(printf '%s|http://192.168.5.1/cgi-bin/luci/admin/nas/fileassistant?path=%s' "${Urls}" "${f}")
    done
    Urls=$( echo "$Urls" | trim ' ' | trim '|' | trim ' ' )
    echo $Urls
}


afunc "$@"
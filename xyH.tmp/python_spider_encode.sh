#!/bin/bash

if [ ! -f "$1" ]; then
    echo "File \"$1\" does not exist."
    exit 1
fi

filesize=$(wc -c "$1" 2>/dev/null | awk '{print $1}')
if (($filesize > 10 * 1024 )); then
    echo "The \"$1\"'s size is too large."
    exit 1
fi

if [[ "${2,,}" != "file" ]] && [[ "${2,,}" != "urls" ]] && [[ "${2,,}" != "both" ]]; then
    echo "The second parameter can only be either \"file\" or \"urls\" or \"both\"."
    exit 1
fi

# https://cn.bing.com/search?pglt=299&q=bash+gen+random+file+name
tmp_file=$(mktemp /tmp/genb64.XXXXXX) || { echo "Failed to create temp file"; exit 1; }
tar -czvf "${tmp_file}" "$1" &> /dev/null
base64Result=$(base64 -w0 "${tmp_file}" 2>/dev/null | awk '{print $1}')
cksumResult=$(echo ${base64Result} | cksum 2> /dev/null | awk '{print $1}')
echo ${cksumResult}-${#base64Result}-${base64Result}-${2,,}
trap 'rm -f -- "${tmp_file}"' EXIT

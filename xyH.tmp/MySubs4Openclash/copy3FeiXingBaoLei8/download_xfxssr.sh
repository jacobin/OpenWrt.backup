#!/bin/bash
## example:
##     download_xfxssr.sh -uhttps://raw.githubusercontent.com/xfxssr/ssnode/main/README.md -oxfxssr.yaml

## https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script
while getopts u:o: flag
do
    case "${flag}" in
        u) url=${OPTARG};;
        o) outFileName=${OPTARG};;
    esac
done

wget "$url" -Owpage.txt
if [ $? -ne 0 ]; then
    echo "download $url failed."
    exit 1
fi

cat wpage.txt | grep "https://www.xfxssr.com/api/v1/client/subscribe" > onlysubs.txt
if [[ -z $(grep '[^[:space:]]' onlysubs.txt) ]] ; then
    echo "There is no subscription link in the file onlysubs.txt"
    exit 2
fi

subs=
while read L; do
    if [ -z "$subs" ]
    then
        subs="$L"
    else
        subs="$subs""|""$L"
    fi
done < onlysubs.txt

source "./generate_download_nodes.sh" "$subs" "$outFileName"
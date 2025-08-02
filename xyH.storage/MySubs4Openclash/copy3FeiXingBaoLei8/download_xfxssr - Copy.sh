#!/bin/bash
## example:
##     download_xfxssr.sh -uhttps://raw.githubusercontent.com/xfxssr/ssnode/main/README.md -oxfxssr.yaml

## https://gist.github.com/jaytaylor/5a90c49e0976aadfe0726a847ce58736
function url_encode() {
    echo "$@" \
        | sed \
            -e 's/%/%25/g' \
            -e 's/ /%20/g' \
            -e 's/!/%21/g' \
            -e 's/"/%22/g' \
            -e "s/'/%27/g" \
            -e 's/#/%23/g' \
            -e 's/(/%28/g' \
            -e 's/)/%29/g' \
            -e 's/+/%2b/g' \
            -e 's/,/%2c/g' \
            -e 's/-/%2d/g' \
            -e 's/:/%3a/g' \
            -e 's/;/%3b/g' \
            -e 's/?/%3f/g' \
            -e 's/@/%40/g' \
            -e 's/\$/%24/g' \
            -e 's/\&/%26/g' \
            -e 's/\*/%2a/g' \
            -e 's/\./%2e/g' \
            -e 's/\//%2f/g' \
            -e 's/\[/%5b/g' \
            -e 's/\\/%5c/g' \
            -e 's/\]/%5d/g' \
            -e 's/\^/%5e/g' \
            -e 's/_/%5f/g' \
            -e 's/`/%60/g' \
            -e 's/{/%7b/g' \
            -e 's/|/%7c/g' \
            -e 's/}/%7d/g' \
            -e 's/~/%7e/g' \
            -e 's/=/%3d/g'
}

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

suburl=`url_encode "$subs"`

## https://stackoverflow.com/questions/7729023/how-do-i-break-up-an-extremely-long-string-literal-in-bash
suburl2="http://127.0.0.1:25500/sub?target=clash&config=ACL4SSR_Online_Full_Adb"`
        `"lockPlus.ini&enable_filter=true&filter_script=function%20filter%28nod"`
        `"e%29%20%7B%0A%20%20%20%20if%28node.Type.toLowerCase%28%29%20%3D%3D%3D"`
        `"%20%22ss%22%20%26%26%20node.EncryptMethod.toLowerCase%28%29%20%3D%3D%"`
        `"3D%20%22chacha20-poly1305%22%29%20%7B%0A%20%20%20%20%20%20%20%20retur"`
        `"n%20false%3B%0A%20%20%20%20%7D%0A%20%20%20%20return%20true%3B%0A%7D&e"`
        `"xclude=%28%E4%B8%AD%E5%9C%8B%7C%E9%A6%99%E6%B8%AF%7C%E4%B8%AD%E5%9B%B"`
        `"D%7CCN%7CHK%7CHong%20Kong%7CHongKong%7C%E5%B9%BF%E4%B8%9C%7C%E8%B4%B5"`
        `"%E5%B7%9E%7C%E5%8C%97%E4%BA%AC%7C%E4%B8%8A%E6%B5%B7%7C%E7%A7%BB%E5%8A"`
        `"%A8%7Cv2cross%29&append_type=true&emoji=true&list=false&udp=true&tfo="`
        `"true&scv=true&fdn=true"
suburl="$suburl2""&url=""$suburl"

wget "$suburl" -OnodesTmp.yaml

if [[ -z $(grep '[^[:space:]]' nodesTmp.yaml) ]] ; then
    echo "No nodes are downloaded"
    exit 3
fi

rm wpage.txt
rm onlysubs.txt

rm "$outFileName"
mv nodesTmp.yaml "$outFileName"

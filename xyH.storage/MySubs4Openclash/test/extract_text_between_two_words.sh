#!/bin/bash
# https://stackoverflow.com/questions/13242469/how-to-use-sed-grep-to-extract-text-between-two-words
# echo "Here is a string" | grep -o -P '(?<=Here).*(?=string)'
# echo 'Here is a string, and Here is another string.' | grep -oP '(?<=Here).*(?=string)' # Greedy match
# echo "Here is a one is a String" | sed -e 's/Here\(.*\)String/\1/'

# A="a href="
# B="title="
#  echo "<p class=\"item-title\"><a href=\"https://nodefree.org/p/2067.html\" title=\"「5月25日」最高速度13.56M/S，2024年最新高速SSR/V2ray/Clash订阅链接免费节点\">「5月25日」最高速度13.56M/S，2024年最新高速SSR/V2ray/Clash订阅链接免费节点</a></p>" \
#     | sed -e 's/\'$A\'\(.*\)\'$B\'/\1/'

function fnExtractStringBetweenAB() {  # $1/return var, $2/originalString, $3/A string, $4/B string
  # echo $2
  # echo $3
  # echo $4
    foo="$2"
    foo=${foo##*${3}}
    foo=${foo%%${4}*}
  # echo [$foo]
  # echo "${1}='${foo}'"
    eval "${1}='${foo}'"
}

fnExtractStringBetweenAB ret "<p class=\"item-title\"><a href=\"https://nodefree.org/p/2067.html\" title=\"「5月25日」最高速度13.56M/S，2024年最新高速SSR/V2ray/Clash订阅链接免费节点\">「5月25日」最高速度13.56M/S，2024年最新高速SSR/V2ray/Clash订阅链接免费节点</a></p>" \
    "a href=" \
    "title="

echo [${ret}]
ret=`echo $ret | xargs`
echo [${ret}]

date=$(date '+%m月%d日')
echo $date

machinenumber=$(date '+%m')
machinenumber=$(expr $machinenumber + 0)
echo [$machinenumber]

machinenumber=$(expr $(date '+%m') + 0)
echo [$machinenumber]

nozero=$(echo $(date '+%m') | sed 's/^0*//')
echo [$nozero]

trimed=$(echo "[abc[defg] " | tr -d "[" | tr -d "]")
echo +${trimed}+

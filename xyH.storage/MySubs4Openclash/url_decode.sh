#!/bin/bash

#                 ## https://stackoverflow.com/questions/6250698/how-to-decode-url-encoded-string-in-shell
#                 #function urldecode() { local i="${*//+/ }"; echo -e "${i//%/\\x}"; }
#
#                 function urlencode() {
#                     # urlencode <string>
#                     local length="${#1}"
#                     for (( i = 0; i < length; i++ )); do
#                         local c="${1:i:1}"
#                         case $c in
#                             [a-zA-Z0-9.~_-]) printf "$c" ;;
#                             *) printf '%%%02X' "'$c" ;;
#                         esac
#                     done
#                 }
#
#                 function urldecode() {
#                     # urldecode <string>
#
#                     local url_encoded="${1//+/ }"
#                     printf '%b' "${url_encoded//%/\\x}"
#                 }
#
#                 decodeURL() { printf "%b\n" "$(sed 's/+/ /g; s/%\([0-9a-f][0-9a-f]\)/\\x\1/g;')"; }
#
#                 x="trojan://JTjS4nBTX@163.177.46.183:28113?allowInsecure=1&peer=download.windowsupdate.com#IEPL+%C2%B7+%E6%97%A5%E6%9C%ACJP+%C2%B7+23+%C2%B7+%E6%B7%B1%E6%B8%AFIEPL"
#                 #y=$(urldecode "$x")
#                 #echo "$y"
#
#                 decodeURL <<< 'trojan://JTjS4nBTX@163.177.46.183:28113?allowInsecure=1&peer=download.windowsupdate.com#IEPL+%C2%B7+%E6%97%A5%E6%9C%ACJP+%C2%B7+23+%C2%B7+%E6%B7%B1%E6%B8%AFIEPL'
#                 decodeURL <<< 'hello+%26+world'
#                 # trojan://JTjS4nBTX@163.177.46.183:28113?allowInsecure=1&peer=download.windowsupdate.com#IEPL · 日本JP · 23 · 深港IEPL
#                 # trojan://JTjS4nBTX@163.177.46.183:28113?allowInsecure=1&peer=download.windowsupdate.com#IEPL+·+日本JP+·+23+·+深港IEPL

    #!/bin/bash
    #
    # Enconding e Decoding de URL com sed
    #
    # Por Daniel Cambría
    # daniel.cambria@bureau-it.com
    #
    # jul/2021

    function url_decode() {
    echo "$@" \
        | sed -E 's/%([0-9a-fA-F]{2})/\\x\1/g;s/\+/ /g'
    }

    function url_encode() {
        # Conforme RFC 3986
        echo "$@" \
        | sed \
        -e 's/ /%20/g' \
        -e 's/:/%3A/g' \
        -e 's/,/%2C/g' \
        -e 's/\?/%3F/g' \
        -e 's/#/%23/g' \
        -e 's/\[/%5B/g' \
        -e 's/\]/%5D/g' \
        -e 's/@/%40/g' \
        -e 's/!/%41/g' \
        -e 's/\$/%24/g' \
        -e 's/&/%26/g' \
        -e "s/'/%27/g" \
        -e 's/(/%28/g' \
        -e 's/)/%29/g' \
        -e 's/\*/%2A/g' \
        -e 's/\+/%2B/g' \
        -e 's/,/%2C/g' \
        -e 's/;/%3B/g' \
        -e 's/=/%3D/g'
    }

    trojanstring="trojan://JTjS4nBTX@163.177.46.183:28113?allowInsecure=1&peer=download.windowsupdate.com#IEPL+%C2%B7+%E6%97%A5%E6%9C%ACJP+%C2%B7+23+%C2%B7+%E6%B7%B1%E6%B8%AFIEPL"
    EscAdd="$(echo $trojanstring | sed 's/+/%2B/g')"
    echo $EscAdd
    echo -e "URL decode: " "$(url_decode \"$EscAdd\")"

  # echo -e "URL decode: " $(url_decode "trojan://JTjS4nBTX@163.177.46.183:28113?allowInsecure=1&peer=download.windowsupdate.com#IEPL+%C2%B7+%E6%97%A5%E6%9C%ACJP+%C2%B7+23+%C2%B7+%E6%B7%B1%E6%B8%AFIEPL")
  # echo -e "URL decode: " $(url_decode "trojan://JTjS4nBTX@163.177.46.183:28113?allowInsecure=1&peer=download.windowsupdate.com#IEPL%2B%C2%B7%2B%E6%97%A5%E6%9C%ACJP%2B%C2%B7%2B23%2B%C2%B7%2B%E6%B7%B1%E6%B8%AFIEPL")
#    echo -e "URL encode: " $(url_encode "$1")
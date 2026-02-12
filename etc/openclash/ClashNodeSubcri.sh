#!/bin/bash


###############################################################################
## 程序流程图 #################################################################
###############################################################################
# https://zhuanlan.zhihu.com/p/54494213
# https://stackoverflow.com/questions/43158140/way-to-create-multiline-comments-in-bash
<< EOF
    original
        --> pass2subconverter
            --> etc_config_openclash.mutable("PLACEHOLDER_ACTIVE_OPENCLASH_CONFIG_PATH")
                --> /etc/config/openclash
EOF


###############################################################################
## 置函数于脚本文件的末尾 #####################################################
###############################################################################
# https://unix.stackexchange.com/questions/724122/is-there-a-way-to-put-helper-functions-at-the-end-of-a-script-file#:~:text=Another%20way%20to%20do%20this,entire%20bash%20script%20in%20functions?
source <(sed '1,/^# HELPER FUNCTIONS #$/d' "$0")


###############################################################################
## 程序运行单例 ###############################################################
###############################################################################
# https://stackoverflow.com/questions/6870221/is-there-any-mutex-semaphore-mechanism-in-shell-scripts
# https://breezetemple.github.io/2018/07/19/shell-flock/
F_LOCK=/var/tmp/$(basename "$0").lock
F_PID=/var/tmp/$(basename "$0").pid
exec 3> ${F_LOCK}
if ! is_not_running; then exit 1; fi


###############################################################################
## 全局变量 ###################################################################
###############################################################################
EXISTENTIAL_CONFIGs="http://127.0.0.1:8080"
# https://www.google.com/search?q=bash+get+absolute+dirname
DIR0=$(dirname "$(readlink -f "$0")")
CONVERTER="http://127.0.0.1:25511"
                         DATA_DIR="/www/Hxy/openclash"
         WEB_ORIG_DAT="http://127.0.0.1/Hxy/openclash/original"
WEB_PASS2SUBCONVERTER="http://127.0.0.1/Hxy/openclash/pass2subconverter"
ACCEPTABLE_DAYs=7


###############################################################################
## 主程序开始运行 #############################################################
###############################################################################
tee_echo "Begin: $(date +%Y%m%d_%H%M%S)"


###############################################################################
## 检查系统的完备性 ###########################################################
###############################################################################
if ! command -v yq &>/dev/null; then
    tee_echo "\tThe YAML command-line tool yq is not installed on the system."
    singleton_clean_up 1
fi

if [ ! -d "${DIR0}/loop6.bak" ]; then
    tee_echo "\tFolder \"${DIR0}/loop6.bak\" not found!"
    singleton_clean_up 1
fi

if [ ! -f "${DIR0}/ClashNodeSubcri.urls" ]; then
    tee_echo "\tFile \"${DIR0}/ClashNodeSubcri.urls\" not found!"
    singleton_clean_up 1
fi

if [ ! -f "${DIR0}/ClashNodeSubcri.etc_config_openclash.const" ]; then
    tee_echo "\tFile \"${DIR0}/ClashNodeSubcri.etc_config_openclash.const\" not found!"
    singleton_clean_up 1
fi

file_hash=$(sha256sum "${DIR0}/ClashNodeSubcri.etc_config_openclash.const" 2>/dev/null | awk '{print $1}')
if [ "$file_hash" != "72336e7ade68ebb895ac9f1e230fa924eebc54e578b39fcf54c8c1ee3b779930" ]; then
    tee_echo "\tThe SHA256 of file \"${DIR0}/ClashNodeSubcri.etc_config_openclash.const\" is incorrect, please check"
    singleton_clean_up 1
fi

if [ ! -d "${DATA_DIR}/original" ]; then
    tee_echo "\tFolder \"${DATA_DIR}/original\" not found!"
    singleton_clean_up 1
fi

if [ ! -d "${DATA_DIR}/pass2subconverter" ]; then
    tee_echo "\tFolder \"${DATA_DIR}/pass2subconverter\" not found!"
    singleton_clean_up 1
fi

#STATUS_CODE=$(curl --output /dev/null --silent --head --write-out "%{http_code}" "http://127.0.0.1)
#if (( STATUS_CODE != 200 )); then
# https://unix.stackexchange.com/questions/86556/testing-remote-tcp-port-using-telnet-by-running-a-one-line-command
r=$(bash -c 'exec 3<> /dev/tcp/127.0.0.1/80;echo $?' 2>/dev/null)
if [ "$r" != "0" ]; then
    tee_echo "\tWeb service \"http://127.0.0.1\" is not started"
    singleton_clean_up 1
fi

STATUS_CODE=$(curl --output /dev/null --silent --head --write-out "%{http_code}" "$EXISTENTIAL_CONFIGs")
if (( STATUS_CODE != 200 )); then
    tee_echo "\tWeb service \"$EXISTENTIAL_CONFIGs\" is not started"
    singleton_clean_up 1
fi

# https://unix.stackexchange.com/questions/86556/testing-remote-tcp-port-using-telnet-by-running-a-one-line-command
r=$(bash -c 'exec 3<> /dev/tcp/127.0.0.1/25511;echo $?' 2>/dev/null)
if [ "$r" != "0" ]; then
    tee_echo "Service \"subconverter:25511\" is not started!"
    singleton_clean_up 1
fi


###############################################################################
## 检查是否有重复的『配置名』##################################################
###############################################################################
clashConfigNames=()
readarray -t arrSubscri < <(cat "${DIR0}/ClashNodeSubcri.urls" | sed -e 's/[[:space:]]*#.*//' -e '/^[[:space:]]*$/d')
subsSize=${#arrSubscri[@]}
if (( subsSize <= 0 )); then
    tee_echo "\tSubscription configuration item count is 0"
    singleton_clean_up 1
fi
for (( j=0; j<${subsSize}; j++ )); do
    subscri=${arrSubscri[$j]}
    arrSplit=(${subscri//,/ })

    split0=${arrSplit[0]}
    split1=${arrSplit[1]}
    split2=${arrSplit[2]}
    split0=$(echo "${split0}" | xargs)
    split1=$(echo "${split1}" | xargs)
    split2=$(echo "${split2}" | xargs)

    if [[ -z "${split0}" || -z "${split1}" || -n "${split2}" ]]; then
        tee_echo "\tLine format error:\n\t\t${subscri}"
        singleton_clean_up 1
    fi

    configFNameDotExtension=${split1}
    # https://stackoverflow.com/questions/965053/extract-filename-and-extension-in-bash
    configFName="${configFNameDotExtension%.*}"
    # https://www.google.com/search?q=bash+trim+string&pws=0&gl=us&gws_rd=cr
    clashConfigNames[$j]=$(echo "${configFName}" | xargs)
done

declare -A uniqClashConfigNames
for ip in "${clashConfigNames[@]}"; do uniqClashConfigNames[$ip]=0; done
if (( ${#uniqClashConfigNames[@]} < ${#clashConfigNames[@]} )); then
    tee_echo "\tItems with counts (duplicates have count > 1):"
    printf "%s\n" "${clashConfigNames[@]}" | sort | uniq -c | sed '/^      1 /d' | sed 's/^/\t /' | tee -a "${DIR0}/ClashNodeSubcri.log"
    singleton_clean_up 1
fi
unset clashConfigNames


###############################################################################
## 如果连内网都已宕机，那么就取消此次的订阅 ###################################
###############################################################################
readarray -t arrSpeedTestResult < <( wget --no-check-certificate -p -O/dev/null "http://www.baidu.com" --dns-timeout=10 --connect-timeout=10 --read-timeout=10 --tries=3 --waitretry=4 2>&1 | grep -o "[0-9.]\\+ [KM]*B/s" )
speedSize=${#arrSpeedTestResult[@]}
if (( speedSize <= 0 )); then
    tee_echo "\tThe Baidu is NOT available. Exit this time."
    singleton_clean_up 1
fi
unset arrSpeedTestResult; unset speedSize


#    ###############################################################################
#    ## 如果外网尚且可用，那么就取消此次的订阅 #####################################
#    ###############################################################################
#    readarray -t arrSpeedTestResult < <( wget --no-check-certificate -p -O/dev/null "http://www.youtube.com" --dns-timeout=10 --connect-timeout=10 --read-timeout=10 --tries=3 --waitretry=4 2>&1 | grep -o "[0-9.]\\+ [KM]*B/s" )
#    speedSize=${#arrSpeedTestResult[@]}
#    if [[ 0 < ${speedSize} ]]; then
#        tee_echo "\tThe Youtube is still available. Exit this time."
#        singleton_clean_up 1
#    fi
#    unset arrSpeedTestResult; unset speedSize


###############################################################################
## 最多尝试5次，把所订阅的原始的数据下载到本地${DATA_DIR}/original ############
###############################################################################
# https://stackoverflow.com/questions/62021429/why-does-command-line-rm-not-accept-quotation-marks-for-directories-with-spaces
if [ -f "${DIR0}/ClashNodeSubcri.loop"6 ]; then
    mv -f "${DIR0}/ClashNodeSubcri.loop"6 "${DIR0}/loop6.bak/ClashNodeSubcri.loop6.$(date +%Y%m%d_%H%M%S)" &> /dev/null
    tar_old_files "/etc/openclash/loop6.bak/ClashNodeSubcri.loop6" "/etc/openclash/loop6.bak/ClashNodeSubcri.loop6.2*" 5
fi
rm -f "${DIR0}/ClashNodeSubcri.loop"? > /dev/null 2>&1
cp -f "${DIR0}/ClashNodeSubcri.urls" "${DIR0}/ClashNodeSubcri.loop1"
rm "${DIR0}/ClashNodeSubcri.127.urls" > /dev/null 2>&1
for (( i=1; i<=5; i++ )); do
    if ! [ -f "${DIR0}/ClashNodeSubcri.loop$i" ]; then break; fi

    # https://unix.stackexchange.com/questions/485221/read-lines-into-array-one-element-per-line-using-bash
    # https://www.google.com/search?q=bash+read+line+except+comment&pws=0&gl=us&gws_rd=cr
    readarray -t arrSubscri < <(cat "${DIR0}/ClashNodeSubcri.loop$i" | sed -e 's/[[:space:]]*#.*//' -e '/^[[:space:]]*$/d' )
    subsSize=${#arrSubscri[@]}
    if (( subsSize <= 0 )); then break; fi

    let j=$i+1
    for subscri in "${arrSubscri[@]}"; do
        # https://stackoverflow.com/questions/918886/how-do-i-split-a-string-on-a-delimiter-in-bash
        arrSplit=(${subscri//,/ })
        # https://www.google.com/search?q=bash+trim+string&pws=0&gl=us&gws_rd=cr
        url=$(echo "${arrSplit[0]}" | xargs)
        fname=$(echo "${arrSplit[1]}" | xargs)

        if ! wget --no-check-certificate --spider "${url}" 2>/dev/null; then
            echo ${url},${fname} >> "${DIR0}/ClashNodeSubcri.loop$j"
            continue
        fi

        wget --no-check-certificate --dns-timeout=10 --connect-timeout=10 --read-timeout=30 --tries=2 "${url}" -O"${DATA_DIR}/original/${fname}.tmp"
        if ! [[ $? -eq 0 && -f "${DATA_DIR}/original/${fname}.tmp" ]]; then
            echo ${url},${fname} >> "${DIR0}/ClashNodeSubcri.loop$j"
            continue
        fi

        thisFileSize=$(get_file_size "${DATA_DIR}/original/${fname}.tmp")
        if ! [[ 0 < ${thisFileSize} ]]; then
            tee_echo "\tThe size of URL \"${url}\" is zero"
            echo "$(date +%Y%m%d_%H%M%S) ${url}" >> "${DIR0}/ClashNodeSubcri.0size"
            continue
        fi

        oldHash=$(sha256sum "${DATA_DIR}/original/${fname}" 2>/dev/null | awk '{print $1}')
        newHash=$(sha256sum "${DATA_DIR}/original/${fname}.tmp" 2>/dev/null | awk '{print $1}')
        if [[ "$newHash" == "$oldHash" ]]; then
            # https://stackoverflow.com/questions/16391208/print-a-files-last-modified-date-in-bash
            oldFiletime=$(date -r "${DATA_DIR}/original/${fname}" +%s%3N)
            nowDatetime=$(date +%s%3N)
            [[ $((nowDatetime - oldFiletime)) -gt $((${ACCEPTABLE_DAYs}*24*60*60)) ]] && bTooOldFile=true || bTooOldFile=false
            if [[ "${bTooOldFile}" == "true" ]]; then
                tee_echo "\tFile \"${url}\" is too old and has NOT been updated for more than ${ACCEPTABLE_DAYs} days"
                echo "$(date +%Y%m%d_%H%M%S) ${url}" >> "${DIR0}/ClashNodeSubcri.oldsubs"
                continue
            fi
        else
            mv -f "${DATA_DIR}/original/${fname}.tmp" "${DATA_DIR}/original/${fname}"
        fi
        echo "${WEB_ORIG_DAT}/${fname},${fname}" >> "${DIR0}/ClashNodeSubcri.127.urls"
    done
    rm -f "${DATA_DIR}/original/"*".tmp" > /dev/null 2>&1
done


###############################################################################
## 把哪些『不能“通过Openclash进行订阅”』的数据文件进行base64的编码转换到${DATA_DIR}/pass2subconverter
###############################################################################
rm "${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls" > /dev/null 2>&1
readarray -t arrSubscri < <(cat "${DIR0}/ClashNodeSubcri.127.urls")
for subscri in "${arrSubscri[@]}"; do
    arrSplit=(${subscri//,/ })
    fname=${arrSplit[1]}
    operation="ln"
    assert_true "[ -f \"${DATA_DIR}/original/${fname}\" ]" "File \"${DATA_DIR}/original/${fname}\" that should exist does not exist"
    if base64 --decode --ignore-garbage "${DATA_DIR}/original/${fname}" > "${DATA_DIR}/original/${fname}.base64decode.result" 2>/dev/null; then
        # https://fabianlee.org/2024/06/22/yq-validate-yaml-syntax
        if yq --exit-status 'tag == "!!map" or tag== "!!seq"' "${DATA_DIR}/original/${fname}.base64decode.result" &>/dev/null; then
            ln -sf "${DATA_DIR}/original/${fname}.base64decode.result" "${DATA_DIR}/pass2subconverter/${fname}"
        else
            rm "${DATA_DIR}/original/${fname}.base64decode.result" > /dev/null 2>&1
            ln -sf "${DATA_DIR}/original/${fname}" "${DATA_DIR}/pass2subconverter/${fname}"
        fi
    else
        rm "${DATA_DIR}/original/${fname}.base64decode.result" > /dev/null 2>&1
        if [[ "${fname}" == *.yaml || "${fname}" == *.yml ]] || yq --exit-status 'tag == "!!map" or tag== "!!seq"' "${DATA_DIR}/original/${fname}" &>/dev/null; then
            ln -sf "${DATA_DIR}/original/${fname}" "${DATA_DIR}/pass2subconverter/${fname}"
        else
            base64 -w0 "${DATA_DIR}/original/${fname}" > "${DATA_DIR}/pass2subconverter/${fname}"
            operation="base64"
        fi
    fi
    assert_true "[[ $? -eq 0 ]]" "Operation \"${operation}\" on file \"${DATA_DIR}/original/${fname}\" failed"
    echo "${WEB_PASS2SUBCONVERTER}/${fname},${fname}" >> "${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls"
done


###############################################################################
## 生成 "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable" ################
###############################################################################
if [ ! -f "${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls" ]; then
    tee_echo "\tFile \"${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls\" not found!"
    singleton_clean_up 1
fi

rm "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable" > /dev/null 2>&1
echo -e "\toption config_path 'PLACEHOLDER_ACTIVE_OPENCLASH_CONFIG_PATH'\n" >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"

clashConfigNames=()
readarray -t arrSubscri < <(cat "${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls")
subsSize=${#arrSubscri[@]}
for (( j=0; j<${subsSize}; j++ )); do
    subscri=${arrSubscri[$j]}
    arrSplit=(${subscri//,/ })
    url=${arrSplit[0]}
    configFNameDotExtension=${arrSplit[1]}
    if ! [[ "${configFNameDotExtension}" == *.yaml || "${configFNameDotExtension}" == *.yml ]]; then
        url_uhttpd=$(urlencode "${url}")
        url="${CONVERTER}/sub?target=clashr&url=${url_uhttpd}"
    fi
    # https://stackoverflow.com/questions/965053/extract-filename-and-extension-in-bash
    configFName="${configFNameDotExtension%.*}"
    # https://www.google.com/search?q=bash+trim+string&pws=0&gl=us&gws_rd=cr
    clashConfigNames[$j]=$(echo "${configFName}" | xargs)
    # https://stackoverflow.com/questions/525872/echo-tab-characters-in-bash-script
    echo -e "config config_subscribe"                    >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
    echo -e "\toption sub_ua 'clash.meta'"               >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
    echo -e "\toption sub_convert '0'"                   >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
    echo -e "\toption enabled '1'"                       >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
    echo -e "\toption name '${clashConfigNames[${j}]}'"  >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
    echo -e "\toption address '${url}'"                  >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
    echo -e ""                                           >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
done

###############################################################################
optNameSize=${#clashConfigNames[@]}
assert_true "[ $optNameSize -gt 0 ]" "The count of configuration items must be greater than 0."
final1=${clashConfigNames[0]}
if (( 1 < ${#clashConfigNames[@]} )); then
    final1=$(combine_subscri "1" "${clashConfigNames[@]}")
fi

###############################################################################
sed -i "s#PLACEHOLDER_ACTIVE_OPENCLASH_CONFIG_PATH#${DIR0}\/config\/${final1}.yaml#g" "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"

###############################################################################
# "${DIR0}/ClashNodeSubcri.cfg"
cat "${DIR0}/ClashNodeSubcri.etc_config_openclash.const"   >  "${DIR0}/ClashNodeSubcri.cfg"
cat "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable" >> "${DIR0}/ClashNodeSubcri.cfg"

###############################################################################
# "/etc/config/openclash"
mv -f "/etc/config/openclash" "/etc/config/openclash.$(date +%Y%m%d_%H%M%S)"
cp -f "${DIR0}/ClashNodeSubcri.cfg" "/etc/config/openclash"


###############################################################################
## 打包多余的config openclash文件。外头只留5个 ###############################
###############################################################################
tar_old_files "/etc/config/openclash.backup" "/etc/config/openclash.2*" 5
tar_old_files "/etc/openclash/yamls" "/etc/openclash/*.yaml" 2
tar_old_files "/etc/openclash/wget.log" "/etc/openclash/wget-log*" 1
tar_old_files "/etc/openclash/config/config_yamls" "/etc/openclash/config/*.yaml" 1


###############################################################################
## 重启 openclash #############################################################
###############################################################################
# "/etc/init.d/openclash" restart;
/usr/share/openclash/openclash.sh > /dev/null 2>&1


###############################################################################
## 主程序运行结束，程序运行单例清场 ###########################################
###############################################################################
singleton_clean_up 0


exit 0
# HELPER FUNCTIONS #

###############################################################################
######################### function: is_not_running ############################
###############################################################################
function is_not_running () {
    if ! flock -xn 3
    then
        local pid=$(cat ${F_PID})
        echo "${0} (PID: ${pid}) already running ..."
        return 1
    else
        echo ${$} > ${F_PID}
        return 0
    fi
}

###############################################################################
######################### function: singleton_clean_up ########################
###############################################################################
function singleton_clean_up() {
    tee_echo "\tEnd: $(date +%Y%m%d_%H%M%S)"
    flock -u 3
    exec 4>&-
    rm -f ${F_LOCK}
    rm -f ${F_PID}
    exit "$1"
}


###############################################################################
######################### function: urlencode #################################
###############################################################################
function urlencode() {
    local old_lc_collate=$LC_COLLATE
    LC_COLLATE=C
    local length="${#1}"
    for (( i = 0; i < length; i++ )); do
        local c="${1:i:1}"
        case $c in
            [a-zA-Z0-9.~_-]) printf "%s" "$c" ;;
            ' ') printf "%%20" ;;
            *) printf "%%%02X" "'$c" ;;
        esac
    done
    LC_COLLATE=$old_lc_collate
}


###############################################################################
######################### function: get_file_size #############################
###############################################################################
function get_file_size() {
    local filepath="$1"
    local size=$(wc -c < $filepath)
    echo "$size"
}


###############################################################################
######################### function: combine_subscri ###########################
###############################################################################
# https://askubuntu.com/questions/674333/how-to-pass-an-array-as-function-argument
function combine_subscri() {
    local depth="$1"
    shift

    arr=("$@")
    asize=${#arr[@]}
    declare -i groupCount=$(( (asize+4)/5 ))

    arrGroup=()
    for (( i = 0; i < ${groupCount}; i++ )); do
        begin=$((i*5))
        if (( 5 < asize-begin )); then
            thissize=5
        else
            thissize=$((asize-begin))
        fi
        end=$((begin+thissize))

        thisCombine="${EXISTENTIAL_CONFIGs}/${arr[${begin}]}.yaml"
        for (( j = $((++begin)); j < ${end}; j++ )); do
            thisCombine="${thisCombine}|${EXISTENTIAL_CONFIGs}/${arr[${j}]}.yaml"
        done
        url_uhttpd=$(urlencode "${thisCombine}")
        resultOptName="${depth}$((i+1))"
        arrGroup[${i}]="${resultOptName}"

        echo -e "config config_subscribe"          >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
        echo -e "\toption sub_ua 'clash.meta'"     >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
        echo -e "\toption sub_convert '0'"         >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
        echo -e "\toption enabled '1'"             >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
        echo -e "\toption name '${resultOptName}'" >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
        echo -e "\toption address '${CONVERTER}/sub?target=clashr&config=ACL4SSR_Online_Full_AdblockPlus.ini&emoji=true&list=false&udp=true&tfo=true&scv=true&fdn=true&enable_filter=true&append_type=true&filter_script=function%20filter%28N%29%7Bif%28N.Type%3D%3D%3D0%7C%7CN.Type%3D%3D%3D6%7C%7CN.Type%3D%3D%3D7%7C%7CN.Type%3D%3D%3D8%29%7Breturn%20true%3B%7Dlet%20M%3DN.EncryptMethod%3Bif%28M%3D%3D%3Dnull%7C%7CM.length%3D%3D%3D0%29%7Bif%28N.Type%3D%3D%3D1%29%7Breturn%20true%3B%7Dreturn%20false%3B%7Dlet%20C%3D%5B%27aes-128-cfb%27%2C%27aes-128-ctr%27%2C%27aes-128-gcm%27%2C%27aes-192-cfb%27%2C%27aes-192-ctr%27%2C%27aes-192-gcm%27%2C%27aes-256-cfb%27%2C%27aes-256-ctr%27%2C%27aes-256-gcm%27%2C%27auto%27%2C%27chacha20%27%2C%27chacha20-ietf%27%2C%27chacha20-ietf-poly1305%27%2C%27rc4-md5%27%2C%27xchacha20%27%2C%27xchacha20-ietf-poly1305%27%5D%3Blet%20m%3DM.toLowerCase%28%29%3Bfor%28let%20i%3D0%3Bi%3CC.length%3Bi%2B%2B%29%7Bif%28m%3D%3D%3DC%5Bi%5D%29%7Breturn%20false%3B%7D%7Dreturn%20true%3B%7D&exclude=%28CN%7CHK%7CHong%20Kong%7CHongKong%7Cv2cross%7CHONG%20KONG%7CHONGKONG%7CV2CROSS%7CHongkong%7C%E5%BB%A3%E6%9D%B1%7C%E5%8C%97%E4%BA%AC%7C%E5%B9%BF%E4%B8%9C%7C%E8%B4%B5%E5%B7%9E%7C%E4%B8%8A%E6%B5%B7%7C%E9%A6%99%E6%B8%AF%7C%E7%A7%BB%E5%8B%95%7C%E7%A7%BB%E5%8A%A8%7C%E4%B8%AD%E5%9C%8B%7C%E4%B8%AD%E5%9B%BD%7C%E8%B2%B4%E5%B7%9E%7C%E5%85%8D%E8%B4%B9%7C%E8%AE%A2%E9%98%85%7C%E8%AE%A2%E9%98%85%E9%9A%8F%E6%97%B6%E4%BC%9A%E5%A4%B1%E6%95%88%7C%E6%97%A5%E6%9C%9F%7C%E7%94%B5%E6%8A%A5%7C%E7%94%B5%E6%8A%A5%E7%BE%A4%7CHTTP%7CHTTPS%7CSOCKS5%29&url=${url_uhttpd}'" >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
        echo -e "" >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
    done

    # https://askubuntu.com/questions/385528/how-to-increment-a-variable-in-bash
    ((depth++))

    if (( 1 < groupCount )); then
        echo $(combine_subscri "${depth}" "${arrGroup[@]}")
    else
        echo "${arrGroup[0]}"
    fi
}


###############################################################################
######################### function: assert_true ###############################
###############################################################################
function assert_true() {
    local condition="$1"
    local message="${2:-Assertion failed!}"

    if ! eval "$condition"; then
        tee_echo "\tERROR: ${message}\n\tEnd: $(date +%Y%m%d_%H%M%S)"
        singleton_clean_up 1
    fi
}
## Example usage:
#VALUE=10
#assert_true "[ $VALUE -eq 10 ]" "Value is not 10"
#
#ANOTHER_VALUE=5
#assert_true "[ $ANOTHER_VALUE -gt 10 ]" "Another value is not greater than 10" # This will fail


###############################################################################
######################### function: tee_echo ##################################
###############################################################################
function tee_echo() {
    echo -e "$1" | tee -a "${DIR0}/ClashNodeSubcri.log"
}


###############################################################################
######################### function: tar_old_files #############################
###############################################################################
function tar_old_files() {
    # https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
    tarFPath=$(echo "$1" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    targetFPathMatchingPattern=$(echo "$2" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    nReserve=$(echo "$3" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    folder1="$(dirname "${tarFPath}")"
    folder2="$(dirname "${targetFPathMatchingPattern}")"
    assert_true "[[ ${folder1} == ${folder2} ]]" "\"${folder1}\" and \"${folder2}\" must have the same parent folder"

    # It must be ensured that "tarFPath" is not in the pattern matching of "targetFPathMatchingPattern"

    if [ -f "${tarFPath}.tar.gz" ]; then
        gzip -d "${tarFPath}.tar.gz"
        assert_true "[ ! -f \"${tarFPath}.tar.gz\" ]" "Failed to unzip file \"${tarFPath}.tar.gz\"."
        tar x -v -f "${tarFPath}.tar" -C "/" >/dev/null 2>&1
        assert_true "[ -f \"${tarFPath}.tar\" ]" "tar's behavior towards file \"${tarFPath}.tar\" does not meet expectations."
        rm "${tarFPath}.tar" -f
        assert_true "[ ! -f \"${tarFPath}.tar\" ]" "Delete file \"${tarFPath}.tar\" failed."
    fi

    ListFPathTemp=$(mktemp "${TMPDIR:-/tmp/}$(basename $0).XXXXXXXXXXXX")
    ls -t -r -1 ${targetFPathMatchingPattern} > ${ListFPathTemp} 2>/dev/null
    ls -t -r -1 ${targetFPathMatchingPattern}.2???????_?????? >> ${ListFPathTemp} 2>/dev/null
    readarray -t arrOpenclashConfigBakup < <(cat "${ListFPathTemp}")
    rm "${ListFPathTemp}" -f
    bakSize=${#arrOpenclashConfigBakup[@]}

    NowDatetime="$(date +'%Y%m%d_%H%M%S')"
    for (( j=0; j<bakSize; j++ )); do
        fpath=${arrOpenclashConfigBakup[$j]}
        fpathLen=${#fpath}

        # bRename
        bRename=false
        if (( 15 < fpathLen )); then
            last15chars=${fpath: -15}
            if ! is_valid_datetime "${last15chars}"; then
                bRename=true
            fi
        else
            bRename=true
        fi

        if [[ "${bRename}" == "true" ]]; then
            newFpath="${fpath}.${NowDatetime}"
            mv -f "${fpath}" "${newFpath}" &> /dev/null
            arrOpenclashConfigBakup[$j]="${newFpath}"
        fi
    done

    tar_command_string="tar c -v -f \"${tarFPath}.tar\""
    rm_command_string="rm -f"
    for (( j=0; j<bakSize-nReserve; j++ )); do
        # https://www.google.com/search?q=bash+string+equa+ignore+case&pws=0&gl=us&gws_rd=cr
        tar_command_string="${tar_command_string} \"${arrOpenclashConfigBakup[$j]}\""
        rm_command_string="${rm_command_string} \"${arrOpenclashConfigBakup[$j]}\""
    done
    tar_command_string="${tar_command_string} >/dev/null 2>&1"
    rm_command_string="${rm_command_string} >/dev/null 2>&1"

    if (( nReserve < bakSize )); then
        eval "$tar_command_string"
        eval "$rm_command_string"
        gzip "${tarFPath}.tar"
        assert_true "[[ -f \"${tarFPath}.tar.gz\" && ! -f \"${tarFPath}.tar\" ]]" "Compressed file \"${tarFPath}.tar\" failed."
    fi
}


###############################################################################
######################### function: is_valid_datetime #########################
###############################################################################
function is_valid_datetime() {
    # OpenWrt uses the busybox-date utility to manage time, supporting formats
    # like YYYY-MM-DD hh:mm[:ss], [YYYY.]MM.DD-hh:mm[:ss],
    # or [[[[[YY]YY]MM]DD]hh]mm[.ss]. The command date -s is used to manually
    # set the system time, while ntpd -q -p is used for syncing via NTP.
    date -D "%Y%m%d_%H%M%S" "$1" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        return 0
    fi

    return 1
}
# # Example Usage:
# function Testcase() {
#     if is_valid_datetime "$1"; then
#         echo "'$1' is a valid date."
#     else
#         echo "'$1' is not a valid date."
#     fi
# }
#
# Testcase "20240228_120342"
# Testcase "20240231_120342"
# Testcase "20240232_120342"


###############################################################################
################################## File END ###################################
###############################################################################

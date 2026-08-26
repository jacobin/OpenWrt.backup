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
CVT_PORT=25522
CONVERTER="http://127.0.0.1:${CVT_PORT}"
                         DATA_DIR="/www/Hxy/openclash"
         WEB_ORIG_DAT="http://127.0.0.1/Hxy/openclash/original"
         WEB_SLIC_DAT="http://127.0.0.1/Hxy/openclash/slice"
WEB_PASS2SUBCONVERTER="http://127.0.0.1/Hxy/openclash/pass2subconverter"
ACCEPTABLE_DAYs=7
SLICE_SIZE=20
SUBCONVERTER_SLICE_SIZE=5


tee_echo "Try to synchronize and calibrate time from WAN"
###############################################################################
## 从WAN上同步校准时间 ########################################################
###############################################################################
ntpd -dnq             \
    -p pool.ntp.org   \
    -p 0.pool.ntp.org \
    -p 1.pool.ntp.org \
    -p 2.pool.ntp.org \
    -p 3.pool.ntp.org   &>/dev/null


tee_echo "Main program starts running"
###############################################################################
## 主程序开始运行 #############################################################
###############################################################################
TIMEBEGIN=$(date +%s%3N)
tee_echo "Begin: $(date +%Y%m%d_%H%M%S)"


tee_echo "Check system integrity"
###############################################################################
## 检查系统的完备性 ###########################################################
###############################################################################
cmds=("yq" "cat" "curl" "wget" "grep" "sed" "xargs" "sort" "uniq" "tee" "mv" "rm" "cp" "awk" "base64" "ln" "flock" "date" "ls" "cut" "expr" "gzip" "eval" "python")
for cmd in "${cmds[@]}"; do
    if ! command -v ${cmd} &>/dev/null; then tee_echo "\tThe command-line tool ${cmd} is not installed on the system."; singleton_clean_up 1; fi
done

existing_dirs=("${DIR0}/loop6.bak" "${DATA_DIR}" "${DATA_DIR}/original" "${DATA_DIR}/slice" "${DATA_DIR}/pass2subconverter")
for dir in "${existing_dirs[@]}"; do mkdir -p "${dir}" > /dev/null 2>&1; done
for dir in "${existing_dirs[@]}"; do
    if [ ! -d "${dir}" ]; then
        tee_echo "\tFolder \"${dir}\" not found!"
        singleton_clean_up 1
    fi
done

existing_files=("${DIR0}/ClashNodeSubcri.urls" "${DIR0}/ClashNodeSubcri.etc_config_openclash.const" "${DIR0}/ClashNodeSubcri.sliceyaml.py")
for fiLe in "${existing_files[@]}"; do
    if [ ! -f "${fiLe}" ]; then
        tee_echo "\tFile \"${fiLe}\" not found!"
        singleton_clean_up 1
    fi
done

file_hash=$(sha256sum "${DIR0}/ClashNodeSubcri.etc_config_openclash.const" 2>/dev/null | awk '{print $1}')
if [ "$file_hash" != "2c92ca6c301f7a927821002bfc43ba26988d314ef869645c6b3e2a29a6ab44f1" ]; then
    tee_echo "\tThe SHA256 of file \"${DIR0}/ClashNodeSubcri.etc_config_openclash.const\" is incorrect, please check"
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
r=$(bash -c 'exec 3<> /dev/tcp/127.0.0.1/'$CVT_PORT';echo $?' 2>/dev/null)
if [ "$r" != "0" ]; then
    tee_echo "Service \"subconverter:${CVT_PORT}\" is not started!"
    singleton_clean_up 1
fi


tee_echo "Check for duplicate 'configuration names'"
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

   #if [[ -z "${split0}" || -z "${split1}" || -n "${split2}" ]]; then
    if [[ -z "${split0}" || -z "${split1}" ]]; then
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


tee_echo "Check for available domain name servers"
###############################################################################
## 检查有否可用的域名服务器 ###################################################
###############################################################################
directDns=
dnsServers=("211.136.192.6" "211.139.136.68" "114.114.114.114" "114.114.115.115" "223.5.5.5" "223.6.6.6" "119.29.29.29" "1.2.4.8" "210.2.4.8" "114.114.114.119" "114.114.115.119" "211.138.180.2" "211.138.180.3" "211.136.192.6" "211.136.20.203")
for dns in "${dnsServers[@]}"; do
    if checkIP ${dns}; then
        directDns=${dns}
        break;
    fi
done
if [ -z "${directDns}" ]; then
    tee_echo "\tNo available DNS."; singleton_clean_up 1;
fi


tee_echo "If the intranet is down, cancel the subscription."
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


#    tee_echo "If the external network is still available, cancel the subscription."
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


tee_echo "Download the subscribed raw data to local ${DATA_DIR}/original after a maximum of 5 attempts."
###############################################################################
## 最多尝试5次，把所订阅的原始的数据下载到本地${DATA_DIR}/original ############
###############################################################################
# https://stackoverflow.com/questions/62021429/why-does-command-line-rm-not-accept-quotation-marks-for-directories-with-spaces
if [ -f "${DIR0}/ClashNodeSubcri.loop"6 ]; then
    mv -f "${DIR0}/ClashNodeSubcri.loop"6 "${DIR0}/loop6.bak/ClashNodeSubcri.loop6.$(date +%Y%m%d_%H%M%S)" &> /dev/null
    tar_old_files "/etc/openclash/loop6.bak/ClashNodeSubcri.loop6" "/etc/openclash/loop6.bak/ClashNodeSubcri.loop6.2*" 5 20
fi
rm -f "${DIR0}/ClashNodeSubcri.loop"? > /dev/null 2>&1
cp -f "${DIR0}/ClashNodeSubcri.urls" "${DIR0}/ClashNodeSubcri.loop1" &> /dev/null
rm "${DIR0}/ClashNodeSubcri.127.urls" > /dev/null 2>&1
for (( i=1; i<=5; i++ )); do
    tee_echo "Loop${i}"
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
        tobe_sliced=$(echo "${arrSplit[2]}" | xargs)

        tee_echo2 "$(GetTitle ${fname} 60)"

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
            mv -f "${DATA_DIR}/original/${fname}.tmp" "${DATA_DIR}/original/${fname}" &> /dev/null
        fi

        if [[ -z "${tobe_sliced}" ]]; then
            echo "${WEB_ORIG_DAT}/${fname},${fname}" >> "${DIR0}/ClashNodeSubcri.127.urls"
        else
            targetDisasFPath="${DATA_DIR}/original/${fname}"

            # If the file is base64 encoded...
            rm -f "${DATA_DIR}/original/${fname}.base64decode.result" &> /dev/null
            if base64 --decode --ignore-garbage "${targetDisasFPath}" > "${DATA_DIR}/original/${fname}.base64decode.result" 2>/dev/null; then
                # https://fabianlee.org/2024/06/22/yq-validate-yaml-syntax
                targetDisasFPath="${DATA_DIR}/original/${fname}.base64decode.result"
            fi

            # If it is a YAML file format ...
            if yq --exit-status 'tag == "!!map" or tag== "!!seq"' "${targetDisasFPath}" &>/dev/null; then
                # Slicing the node data of yaml
                readarray -t arrSliceYaml < <( python "${DIR0}/ClashNodeSubcri.sliceyaml.py" "-i${targetDisasFPath}" "-o${DATA_DIR}/slice" "-f${fname}" -z${SLICE_SIZE} )
                if [ -f "${DATA_DIR}/slice/${arrSliceYaml[0]}" ]; then
                    for aSlice in "${arrSliceYaml[@]}"; do
                        assert_true "[ -f \"${DATA_DIR}/slice/${aSlice}\" ]" "File \"${DATA_DIR}/slice/${aSlice}\" that should exist does not exist"
                        echo "${WEB_SLIC_DAT}/${aSlice},${aSlice}" >> "${DIR0}/ClashNodeSubcri.127.urls"
                    done
                fi
            else
                # Slicing the node data of v2ray
                lineNo=1
                fileNo=1
                readarray -t v2rayLines < <(cat "${targetDisasFPath}" | sort -u)
                for v2rayLine in "${v2rayLines[@]}"; do
                    v2rayLine=$(trimstring "${v2rayLine}")
                    if ! [[ ${v2rayLine} == \#* || ${v2rayLine} == "ss://"* ]]; then
                        if (( lineNo % ${SLICE_SIZE} == 1 )); then
                            newSubFName=${fname}.$(printf %05d ${fileNo}).txt
                            echo "${WEB_SLIC_DAT}/${newSubFName},${newSubFName}" >> "${DIR0}/ClashNodeSubcri.127.urls"
                            rm -f "${DATA_DIR}/slice/${newSubFName}" &> /dev/null
                            echo "$v2rayLine" > "${DATA_DIR}/slice/${newSubFName}"
                            ((fileNo++))
                        else
                            echo "$v2rayLine">> "${DATA_DIR}/slice/${newSubFName}"
                        fi
                        ((lineNo++))
                    fi
                done
            fi
        fi

    done
    rm -f "${DATA_DIR}/original/"*".tmp" > /dev/null 2>&1
done


tee_echo "Convert data files that 'cannot be subscribed to via Openclash' to ${DATA_DIR}/pass2subconverter using base64 encoding."
###############################################################################
## 把哪些『不能“通过Openclash进行订阅”』的数据文件进行base64的编码转换到${DATA_DIR}/pass2subconverter
###############################################################################
rm -f "${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls" > /dev/null 2>&1
readarray -t arrSubscri < <(cat "${DIR0}/ClashNodeSubcri.127.urls")

if [ ${#arrSubscri[@]} -le 0 ]; then
    tee_echo "\tNo valid download, program exits.!"
    singleton_clean_up 1
fi

for subscri in "${arrSubscri[@]}"; do
    arrSplit=(${subscri//,/ })
    fname=${arrSplit[1]}
    url127=${arrSplit[0]}
    folderName=$( tweezers_original_folder_name "${url127}" )
    operation="ln"
    assert_true "[ -f \"${DATA_DIR}/${folderName}/${fname}\" ]" "File \"${DATA_DIR}/${folderName}/${fname}\" that should exist does not exist"
    rm -f "${DATA_DIR}/${folderName}/${fname}.base64decode.result" &> /dev/null
    if base64 --decode --ignore-garbage "${DATA_DIR}/${folderName}/${fname}" > "${DATA_DIR}/${folderName}/${fname}.base64decode.result" 2>/dev/null; then
        # https://fabianlee.org/2024/06/22/yq-validate-yaml-syntax
        if yq --exit-status 'tag == "!!map" or tag== "!!seq"' "${DATA_DIR}/${folderName}/${fname}.base64decode.result" &>/dev/null; then
            ln -sf "${DATA_DIR}/${folderName}/${fname}.base64decode.result" "${DATA_DIR}/pass2subconverter/${fname}" &> /dev/null
        else
            rm -f "${DATA_DIR}/${folderName}/${fname}.base64decode.result" > /dev/null 2>&1
            ln -sf "${DATA_DIR}/${folderName}/${fname}" "${DATA_DIR}/pass2subconverter/${fname}" &> /dev/null
        fi
    else
        rm -f "${DATA_DIR}/${folderName}/${fname}.base64decode.result" > /dev/null 2>&1
        if [[ "${fname}" == *.yaml || "${fname}" == *.yml ]] || yq --exit-status 'tag == "!!map" or tag== "!!seq"' "${DATA_DIR}/${folderName}/${fname}" &>/dev/null; then
            ln -sf "${DATA_DIR}/${folderName}/${fname}" "${DATA_DIR}/pass2subconverter/${fname}"  &> /dev/null
        else
            rm -f "${DATA_DIR}/pass2subconverter/${fname}" > /dev/null 2>&1
            base64 -w0 "${DATA_DIR}/${folderName}/${fname}" > "${DATA_DIR}/pass2subconverter/${fname}"
            operation="base64"
        fi
    fi
    assert_true "[[ $? -eq 0 ]]" "Operation \"${operation}\" on file \"${DATA_DIR}/${folderName}/${fname}\" failed"
    echo "${WEB_PASS2SUBCONVERTER}/${fname},${fname}" >> "${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls"
done


tee_echo "Generate '${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable'."
###############################################################################
## 生成 "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable" ################
###############################################################################
if [ ! -f "${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls" ]; then
    tee_echo "\tFile \"${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls\" not found!"
    singleton_clean_up 1
fi

rm -f "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable" > /dev/null 2>&1
echo -e "\toption config_path 'PLACEHOLDER_ACTIVE_OPENCLASH_CONFIG_PATH'\n" >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
echo -e "\toption custom_domain_dns_server '${directDns}'\n" >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"

clashConfigNames=()
readarray -t arrSubscri < <(cat "${DIR0}/ClashNodeSubcri.127.pass2subconverter.urls")
subsSize=${#arrSubscri[@]}
tee_echo "\tsubsSize:${subsSize}"

if [ ${subsSize} -le 0 ]; then
    tee_echo "\tThe number of PASS2SUBCONVERTERS is zero.!"
    singleton_clean_up 1
fi

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
rm -f "${DIR0}/ClashNodeSubcri.cfg" &> /dev/null
cat "${DIR0}/ClashNodeSubcri.etc_config_openclash.const"   >  "${DIR0}/ClashNodeSubcri.cfg"
cat "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable" >> "${DIR0}/ClashNodeSubcri.cfg"

###############################################################################
# "/etc/config/openclash"
mv -f "/etc/config/openclash" "/etc/config/openclash.$(date +%Y%m%d_%H%M%S)" &> /dev/null
cp -f "${DIR0}/ClashNodeSubcri.cfg" "/etc/config/openclash" &> /dev/null


tee_echo "Package redundant config Openclash files. Only 5 external files are left."
###############################################################################
## 打包多余的config openclash文件。外头只留5个 ###############################
###############################################################################
tar_old_files "/etc/config/openclash.backup" "/etc/config/openclash.2*" 5 20
tar_old_files "/etc/openclash/yamls" "/etc/openclash/*.yaml" 2 20
tar_old_files "/etc/openclash/wget.log" "/etc/openclash/wget-log*" 1 20
tar_old_files "/etc/openclash/config/config_yamls" "/etc/openclash/config/*.yaml" 1 20


tee_echo "Restart Openclash."
###############################################################################
## 重启 openclash #############################################################
###############################################################################
# "/etc/init.d/openclash" restart
/usr/share/openclash/openclash.sh > /dev/null 2>&1


tee_echo "Main program finishes running."
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
    timeEnd=$(date +%s%3N)
    total_seconds=$((timeEnd-TIMEBEGIN))
    seconds=$((total_seconds % 60))
    minutes=$(((total_seconds / 60) % 60))
    hours=$((total_seconds / 3600))
    printf -v formatted_string "%02d:%02d:%02d" $hours $minutes $seconds
    tee_echo "\tEnd: $(date +%Y%m%d_%H%M%S), time escaped:${formatted_string}"
    flock -u 3
    exec 4>&-
    rm -f ${F_LOCK} &> /dev/null
    rm -f ${F_PID} &> /dev/null
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
    declare -i groupCount=$(( (asize+SUBCONVERTER_SLICE_SIZE-1)/SUBCONVERTER_SLICE_SIZE ))

    arrGroup=()
    for (( i = 0; i < ${groupCount}; i++ )); do
        begin=$((i*SUBCONVERTER_SLICE_SIZE))
        if (( SUBCONVERTER_SLICE_SIZE < asize-begin )); then
            thissize=SUBCONVERTER_SLICE_SIZE
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
        echo -e "\toption address '${CONVERTER}/sub?target=clashr&config=ACL4SSR_Online_Full_AdblockPlus.ini&emoji=true&list=false&udp=true&tfo=true&scv=true&fdn=true&enable_filter=true&append_type=true&filter_script=function%20filter%28N%29%7Bif%28N.Type%3D%3D%3D0%7C%7CN.Type%3D%3D%3D1%7C%7CN.Type%3D%3D%3D2%7C%7CN.Type%3D%3D%3D4%7C%7CN.Type%3D%3D%3D6%7C%7CN.Type%3D%3D%3D7%7C%7CN.Type%3D%3D%3D8%29%7Breturn%20true%3B%7Dlet%20M%3DN.EncryptMethod%3Bif%28M%3D%3D%3Dnull%7C%7CM.length%3D%3D%3D0%29%7Bif%28N.Type%3D%3D%3D1%29%7Breturn%20true%3B%7Dreturn%20false%3B%7Dlet%20C%3D%5B%27aes-128-cfb%27%2C%27aes-128-ctr%27%2C%27aes-128-gcm%27%2C%27aes-192-cfb%27%2C%27aes-192-ctr%27%2C%27aes-192-gcm%27%2C%27aes-256-cfb%27%2C%27aes-256-ctr%27%2C%27aes-256-gcm%27%2C%27auto%27%2C%27chacha20%27%2C%27chacha20-ietf%27%2C%27chacha20-ietf-poly1305%27%2C%27rc4-md5%27%2C%27xchacha20%27%2C%27xchacha20-ietf-poly1305%27%5D%3Blet%20m%3DM.toLowerCase%28%29%3Bfor%28let%20i%3D0%3Bi%3CC.length%3Bi%2B%2B%29%7Bif%28m%3D%3D%3DC%5Bi%5D%29%7Breturn%20false%3B%7D%7Dreturn%20true%3B%7D&exclude=%28CN%7CHK%7CHong%20Kong%7CHongKong%7Cv2cross%7CHONG%20KONG%7CHONGKONG%7CV2CROSS%7CHongkong%7C%E5%BB%A3%E6%9D%B1%7C%E5%8C%97%E4%BA%AC%7C%E5%B9%BF%E4%B8%9C%7C%E8%B4%B5%E5%B7%9E%7C%E4%B8%8A%E6%B5%B7%7C%E9%A6%99%E6%B8%AF%7C%E7%A7%BB%E5%8B%95%7C%E7%A7%BB%E5%8A%A8%7C%E4%B8%AD%E5%9C%8B%7C%E4%B8%AD%E5%9B%BD%7C%E8%B2%B4%E5%B7%9E%7C%E5%85%8D%E8%B4%B9%7C%E8%AE%A2%E9%98%85%7C%E8%AE%A2%E9%98%85%E9%9A%8F%E6%97%B6%E4%BC%9A%E5%A4%B1%E6%95%88%7C%E6%97%A5%E6%9C%9F%7C%E7%94%B5%E6%8A%A5%7C%E7%94%B5%E6%8A%A5%E7%BE%A4%7CHTTP%7CHTTPS%7CSOCKS5%29&url=${url_uhttpd}'" >> "${DIR0}/ClashNodeSubcri.etc_config_openclash.mutable"
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
        tee_echo "\tERROR: ${message}\n"
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
    echo -e $(date "+%Y-%m-%d %H:%M:%S $1") | tee -a "${DIR0}/ClashNodeSubcri.log"
}

function tee_echo2() {
    echo -e "\n\n\n"
    echo -e $(date "+%Y-%m-%d %H:%M:%S $1") | tee -a "${DIR0}/ClashNodeSubcri.log"
}


###############################################################################
######################### function: tar_old_files #############################
###############################################################################
function tar_old_files() {
    # https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
    tarFPath=$(echo "$1" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    targetFPathMatchingPattern=$(echo "$2" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    nOutside=$(echo "$3" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    nReserve=$(echo "$4" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # {0/filetime0}  {coordA/filetimeA}          coordB/filetimeB}
    #   ^                   ^                          ^
    #   |-------------------------- bakSize ---------------------------------|
    #                                                  |<----- nOutside ---->|
    #                       |<-------------- nReserve ---------------------->|
    assert_true "(( ${nReserve} > ${nOutside} ))" "The number of files to be retained is less than the number of files to be left outside the package; this is incorrect."

    folder1="$(dirname "${tarFPath}")"
    folder2="$(dirname "${targetFPathMatchingPattern}")"
    assert_true "[[ ${folder1} == ${folder2} ]]" "\"${folder1}\" and \"${folder2}\" must have the same parent folder"

    # It must be ensured that "tarFPath" is not in the pattern matching of "targetFPathMatchingPattern"

    if [ -f "${tarFPath}.tar.gz" ]; then
        gzip -d "${tarFPath}.tar.gz" &> /dev/null
        assert_true "[ ! -f \"${tarFPath}.tar.gz\" ]" "Failed to unzip file \"${tarFPath}.tar.gz\"."
        tar x -v -f "${tarFPath}.tar" -C "/" >/dev/null 2>&1
        assert_true "[ -f \"${tarFPath}.tar\" ]" "tar's behavior towards file \"${tarFPath}.tar\" does not meet expectations."
        rm -f "${tarFPath}.tar" &> /dev/null
        assert_true "[ ! -f \"${tarFPath}.tar\" ]" "Delete file \"${tarFPath}.tar\" failed."
    fi

    ListFPathTemp=$(mktemp "${TMPDIR:-/tmp/}$(basename $0).XXXXXXXXXXXX")
    ls -t -r -1 ${targetFPathMatchingPattern} > ${ListFPathTemp} 2>/dev/null
    ls -t -r -1 ${targetFPathMatchingPattern}.2???????_?????? >> ${ListFPathTemp} 2>/dev/null
    readarray -t arrOpenclashConfigBakup < <(cat "${ListFPathTemp}")
    rm -f "${ListFPathTemp}" &> /dev/null
    bakSize=${#arrOpenclashConfigBakup[@]}
    if (( bakSize == 0 )); then return; fi

    coordB=$((bakSize-nOutside))
    if (( coordB <= 0  )); then return; fi
    coordA=$((bakSize-nReserve))
    if (( coordA < 0  )); then let coordA=0; fi
    assert_true "(( $coordA < $coordB ))" ""

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
    for (( j=0; j<coordA; j++ )); do
        rm_command_string="${rm_command_string} \"${arrOpenclashConfigBakup[$j]}\""
    done

    for (( j=coordA; j<coordB; j++ )); do
        # https://www.google.com/search?q=bash+string+equa+ignore+case&pws=0&gl=us&gws_rd=cr
        tar_command_string="${tar_command_string} \"${arrOpenclashConfigBakup[$j]}\""
        rm_command_string="${rm_command_string} \"${arrOpenclashConfigBakup[$j]}\""
    done
    tar_command_string="${tar_command_string} >/dev/null 2>&1"
    rm_command_string="${rm_command_string} >/dev/null 2>&1"

    eval "$tar_command_string"
    eval "$rm_command_string"
    gzip "${tarFPath}.tar"  &> /dev/null
    assert_true "[[ -f \"${tarFPath}.tar.gz\" && ! -f \"${tarFPath}.tar\" ]]" "Compressed file \"${tarFPath}.tar\" failed."
}


###############################################################################
######################### function: LeapYear ##################################
###############################################################################
# https://blog.csdn.net/Stars____/article/details/106972527
function LeapYear() {
    year=$1
    if ( (( year%4==0 )) && (( year%100!=0 )) ) || (( year%400==0 )); then
        return 0 # true
    fi
    return 1 # false
}


###############################################################################
######################### function: MonthDays #################################
###############################################################################
function MonthDays() {
    year=$(expr $1 + 0) # 02 ==> 2
    month=$(expr $2 + 0)
    Days=( 29 31 28 31 30 31 30 31 31 30 31 30 31 )

    if (( 2==$month )) && LeapYear $year; then
        month=0;
    fi

    echo ${Days[$month]}
}


###############################################################################
######################### function: isdigit ###################################
###############################################################################
# https://stackoverflow.com/questions/806906/how-do-i-test-if-a-variable-is-a-number-in-bash
function isdigit() {
    str=$1
    if [[ ! $str =~ ^[0-9]+$ ]]; then
        return 1
    fi
    return 0
}


###############################################################################
######################### function: is_valid_datetime #########################
###############################################################################
# https://blog.csdn.net/weixin_45956148/article/details/107862145
function is_valid_datetime() { # 20260123_102345
    Date=$1

    if [ ${#Date} -ne 15 ];then
        return 1
    fi

    YYYYMMDD=$(echo $Date |cut -c 1-8)
    CONNECTED_CHAR=$(echo $Date |cut -c 9-9)
    hhmmss=$(echo $Date |cut -c 10-15)

    if [ ! $CONNECTED_CHAR=="_" ];then
        return 1
    fi

    if ! isdigit $YYYYMMDD; then
        return 1
    fi

    if ! isdigit $hhmmss; then
        return 1
    fi

      Year=$(echo $Date |cut -c 1-4)
     Month=$(echo $Date |cut -c 5-6)
       Day=$(echo $Date |cut -c 7-8)
      hour=$(echo $Date |cut -c 10-11)
    minute=$(echo $Date |cut -c 12-13)
    second=$(echo $Date |cut -c 14-15)

    if [ ${#YYYYMMDD} -ne 8 ];then
        return 1
    fi

    if [ ${#hhmmss} -ne 6 ];then
        return 1
    fi

      Year=$(expr $Year   + 0)
     Month=$(expr $Month  + 0)
       Day=$(expr $Day    + 0)
      hour=$(expr $hour   + 0)
    minute=$(expr $minute + 0)
    second=$(expr $second + 0)


    if ! { [ $Month -gt 0 -a $Month -le 12 ]; }; then
        return 1
    fi

    Days=$(MonthDays $Year $Month)
    if (( Day <= 0 )) || (( Days < Day )); then
        return 1
    fi

    if (( hour < 0 )) || (( 23 < hour )); then
        return 1
    fi

    if (( minute < 0 )) || (( 59 < minute )); then
        return 1
    fi

    if (( second < 0 )) || (( 59 < second )); then
        return 1
    fi

    return 0
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
######################### function: checkIP ###################################
###############################################################################
# https://stackoverflow.com/questions/6118948/bash-loop-ping-successful
function checkIP() {
    ip=$1
    ((count = 3))                           # Maximum number to try.
    while [[ $count -ne 0 ]] ; do
        ping -c 1 $ip  &>/dev/null          # Try once.
        rc=$?
        if [[ $rc -eq 0 ]] ; then
            ((count = 1))                   # If okay, flag loop exit.
        else
            sleep 1                         # Minimise network storm.
        fi
        ((count = count - 1))               # So we don't go forever.
    done

    if [[ $rc -eq 0 ]] ; then               # Make final determination.
        return 0
    else
        return 1
    fi
}
# -----------------------------------------------------------------------------
# # Example Usage:
# if checkIP "8.8.8.8"; then
#     echo "8.8.8.8" is ok.
# else
#     echo "8.8.8.8" is bad.
# fi
#
# if checkIP "114.114.114.114"; then
#     echo "114.114.114.114" is ok.
# else
#     echo "114.114.114.114" is bad.
# fi

###############################################################################
######################### trimstring ##########################################
###############################################################################
# https://jcgoran.github.io/2021/02/07/bash-string-trimming.html
function trimstring() {
    assert_true "[ $# -eq 1 ]" "USAGE: trimstring [STRING]."
    s="${1}"
    size_before=${#s}
    size_after=0
    while [ ${size_before} -ne ${size_after} ]; do
        size_before=${#s}
        s="${s#[[:space:]]}"
        s="${s%[[:space:]]}"
        size_after=${#s}
    done
    echo "${s}"
    return 0
}

###############################################################################
############### tweezers_original_folder_name #################################
###############################################################################
function tweezers_original_folder_name() {
    assert_true "[ $# -eq 1 ]" "There must be one and only one parameter."
    url127="${1}"
    old_ifs="$IFS"
    IFS="/" read -r -a my_array <<< "${url127}}"
    IFS="$old_ifs"
    echo "${my_array[5]}"
    return 0
}

###############################################################################
######################### GetTitle ############################################
###############################################################################
# $1 -- title, $2 -- total width
function GetTitle() {
    title=$1
    totalWidth=$2
    zTitle=${#title}

    # # aaaaaaaaaaaaa #
    if [[ ${totalWidth} < $((zTitle +4)) ]]; then
        echo "${title}"
        return
    fi

    half=$(( (totalWidth-zTitle) / 2 - 1))
    half2=$((totalWidth-half-1))
    # https://stackoverflow.com/questions/5349718/how-can-i-repeat-a-character-in-bash
    str=$(printf "%${half}s")
    str2=$(printf "%${half2}s")
    echo "${str// /#}" "${title}" "${str// /#}"
}

###############################################################################
################################## File END ###################################
###############################################################################

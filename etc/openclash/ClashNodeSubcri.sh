#!/bin/bash

###############################################################################
######################### class: Process Singleton ############################
###############################################################################
# https://stackoverflow.com/questions/6870221/is-there-any-mutex-semaphore-mechanism-in-shell-scripts
# https://breezetemple.github.io/2018/07/19/shell-flock/
F_LOCK=/var/tmp/$(basename "$0").lock
F_PID=/var/tmp/$(basename "$0").pid

exec 3> ${F_LOCK}

#******************************************************************************
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

#******************************************************************************
function clean_up () {
    flock -u 3
    exec 4>&-
    rm -f ${F_LOCK}
    rm -f ${F_PID}
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
######################### function: combine_openclash_config ##################
###############################################################################
# https://askubuntu.com/questions/674333/how-to-pass-an-array-as-function-argument
function combine_openclash_config() {
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

        thisCombine="http://127.0.0.1:8080/${arr[${begin}]}.yaml"
        for (( j = $((++begin)); j < ${end}; j++ )); do
            thisCombine="${thisCombine}|http://127.0.0.1:8080/${arr[${j}]}.yaml"
        done
        url_uhttpd=$(urlencode "${thisCombine}")
        resultOptName="${depth}$((i+1))"
        arrGroup[${i}]="${resultOptName}"

        echo -e "config config_subscribe"          >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption sub_ua 'clash.meta'"     >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption sub_convert '0'"         >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption enabled '1'"             >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption name '${resultOptName}'" >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption address 'http://127.0.0.1:25511/sub?target=clash&config=ACL4SSR_Online_Full_AdblockPlus.ini&emoji=true&list=false&udp=true&tfo=true&scv=true&fdn=true&enable_filter=true&filter_script=function%20filter%28N%29%7Bif%28N.Type%3D%3D%3D0%29%7Breturn%20true%3B%7Dlet%20M%3DN.EncryptMethod%3Bif%28M%3D%3D%3Dnull%7C%7CM.length%3D%3D%3D0%29%7Bif%28N.Type%3D%3D%3D1%29%7Breturn%20true%3B%7Dreturn%20false%3B%7Dlet%20C%3D%5B%27aes-128-cfb%27%2C%27aes-128-ctr%27%2C%27aes-128-gcm%27%2C%27aes-192-cfb%27%2C%27aes-192-ctr%27%2C%27aes-192-gcm%27%2C%27aes-256-cfb%27%2C%27aes-256-ctr%27%2C%27aes-256-gcm%27%2C%27auto%27%2C%27chacha20%27%2C%27chacha20-ietf%27%2C%27chacha20-ietf-poly1305%27%2C%27rc4-md5%27%2C%27xchacha20%27%2C%27xchacha20-ietf-poly1305%27%5D%3Blet%20m%3DM.toLowerCase%28%29%3Bfor%28let%20i%3D0%3Bi%3CC.length%3Bi%2B%2B%29%7Bif%28m%3D%3D%3DC%5Bi%5D%29%7Breturn%20false%3B%7D%7Dreturn%20true%3B%7D&exclude=%28CN%7CHK%7CHong%20Kong%7CHongKong%7Cv2cross%7CHONG%20KONG%7CHONGKONG%7CV2CROSS%7CHongkong%7C%E5%BB%A3%E6%9D%B1%7C%E5%8C%97%E4%BA%AC%7C%E5%B9%BF%E4%B8%9C%7C%E8%B4%B5%E5%B7%9E%7C%E4%B8%8A%E6%B5%B7%7C%E9%A6%99%E6%B8%AF%7C%E7%A7%BB%E5%8B%95%7C%E7%A7%BB%E5%8A%A8%7C%E4%B8%AD%E5%9C%8B%7C%E4%B8%AD%E5%9B%BD%7C%E8%B2%B4%E5%B7%9E%7C%E5%85%8D%E8%B4%B9%7C%E8%AE%A2%E9%98%85%7C%E8%AE%A2%E9%98%85%E9%9A%8F%E6%97%B6%E4%BC%9A%E5%A4%B1%E6%95%88%7C%E6%97%A5%E6%9C%9F%7C%E7%94%B5%E6%8A%A5%7C%E7%94%B5%E6%8A%A5%E7%BE%A4%29&url=${url_uhttpd}'" >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "" >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
    done

    # https://askubuntu.com/questions/385528/how-to-increment-a-variable-in-bash
    ((depth++))

    if (( 1 < groupCount )); then
        echo $(combine_openclash_config "${depth}" "${arrGroup[@]}")
    else
        echo "${arrGroup[0]}"
    fi
}

###############################################################################
######################### Program Singleton starts running ####################
###############################################################################
if ! is_not_running; then exit 1; fi


###############################################################################
######################### The main program starts running #####################
###############################################################################
echo "Begin: $(date +%Y%m%d_%H%M%S)" | tee -a "/etc/openclash/ClashNodeSubcri.log"

#******************************************************************************
if [ ! -f "/etc/openclash/ClashNodeSubcri.urls" ]; then
    echo -e "\tFile \"/etc/openclash/ClashNodeSubcri.urls\" not found!" | tee -a "/etc/openclash/ClashNodeSubcri.log"
    clean_up
    exit 1
fi

echo 11111111111111111111111111111111111111111111111111111111111111111111111111
#******************************************************************************
# "/etc/openclash/ClashNodeSubcri.down"
# Download the original data file
for (( k=1; k<=6; k++ )); do rm "/etc/openclash/ClashNodeSubcri.loop$k" > /dev/null 2>&1; done
cp -f "/etc/openclash/ClashNodeSubcri.urls" "/etc/openclash/ClashNodeSubcri.loop1"
rm "/etc/openclash/ClashNodeSubcri.down" > /dev/null 2>&1
for (( i=1; i<=5; i++ )); do
    if [ -f "/etc/openclash/ClashNodeSubcri.loop$i" ]; then
        # https://unix.stackexchange.com/questions/485221/read-lines-into-array-one-element-per-line-using-bash
        readarray -t arrSubscri < <(cat "/etc/openclash/ClashNodeSubcri.loop$i")
        subsSize=${#arrSubscri[@]}
        if (( subsSize > 0 )); then
            let j=$i+1
            for subscri in ${arrSubscri[@]}; do
                # https://stackoverflow.com/questions/918886/how-do-i-split-a-string-on-a-delimiter-in-bash
                arrSplit=(${subscri//,/ })
                url=${arrSplit[0]}
                fname=${arrSplit[1]}
                wget --dns-timeout=10 --connect-timeout=10 --read-timeout=30 --tries=5 "${url}" -O"/www/Hxy/openclash/${fname}.tmp"
                if [ $? -eq 0 ]; then
                    mv -f "/www/Hxy/openclash/${fname}.tmp" "/www/Hxy/openclash/${fname}"
                    echo "/www/Hxy/openclash/${fname}" >> "/etc/openclash/ClashNodeSubcri.down"
                else
                    echo ${url},${fname} >> "/etc/openclash/ClashNodeSubcri.loop$j"
                fi
            done
        else
            break
        fi
    fi
done

echo 22222222222222222222222222222222222222222222222222222222222222222222222222
#******************************************************************************
if [ ! -f "/etc/openclash/ClashNodeSubcri.down" ]; then
    echo -e "\tFile \"/etc/openclash/ClashNodeSubcri.down\" not found!" | tee -a "/etc/openclash/ClashNodeSubcri.log"
    clean_up
    exit 1
fi

#******************************************************************************
# "/etc/openclash/ClashNodeSubcri.base64"
rm "/etc/openclash/ClashNodeSubcri.base64" > /dev/null 2>&1
rm "/etc/openclash/ClashNodeSubcri.ymls" > /dev/null 2>&1
readarray -t arrDown < <(cat "/etc/openclash/ClashNodeSubcri.down")
downSize=${#arrDown[@]}
if (( downSize > 0 )); then
    for thisDown in ${arrDown[@]}; do
        if base64 --decode --ignore-garbage "$thisDown" &>/dev/null; then
            echo "$thisDown" >> "/etc/openclash/ClashNodeSubcri.base64"
        else
            if ! [[ "$thisDown" == *.yaml || "$thisDown" == *.yml ]]; then
                base64 -w0 "$thisDown" > "${thisDown}.b64"
                echo "${thisDown}.b64" >> "/etc/openclash/ClashNodeSubcri.base64"
            else
                echo "$thisDown" >> "/etc/openclash/ClashNodeSubcri.ymls"
            fi
        fi
    done
fi

echo 33333333333333333333333333333333333333333333333333333333333333333333333333
#******************************************************************************
# "/etc/openclash/ClashNodeSubcri.ymls"
if [ -f "/etc/openclash/ClashNodeSubcri.base64" ]; then
    readarray -t arrB64 < <(cat "/etc/openclash/ClashNodeSubcri.base64")
    b64Size=${#arrB64[@]}
    if (( b64Size > 0 )); then
        for thisB64 in ${arrB64[@]}; do
            thisUrl=$(sed "s/\/www/http:\/\/127.0.0.1/" <<< ${thisB64})
            url_uhttpd=$(urlencode "${thisUrl}")
            wget --dns-timeout=10 --connect-timeout=10 --read-timeout=30 --tries=5 "http://127.0.0.1:25511/sub?target=clash&url=${url_uhttpd}" -O"${thisB64}.yml"
            if [ $? -eq 0 ]; then
                echo "${thisB64}.yml" >> "/etc/openclash/ClashNodeSubcri.ymls"
            else
                echo -e "\tFailed: wget --dns-timeout=10 --connect-timeout=10 --read-timeout=30 --tries=5 \"http://127.0.0.1:25511/sub?target=clash&url=${url_uhttpd}\" -O\"${thisB64}.yml\"" | tee -a "/etc/openclash/ClashNodeSubcri.log"
            fi
        done
    fi
fi

echo 44444444444444444444444444444444444444444444444444444444444444444444444444
#******************************************************************************
# "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
clashConfigNames=()
rm "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4" > /dev/null 2>&1
echo -e "" >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
if [ -f "/etc/openclash/ClashNodeSubcri.ymls" ]; then
    readarray -t arrYaml < <(cat "/etc/openclash/ClashNodeSubcri.ymls")
    yamlSize=${#arrYaml[@]}
    for (( j=0; j<${yamlSize}; j++ )); do
        thisYaml=${arrYaml[$j]}
        thisUrl=$(sed "s/\/www/http:\/\/127.0.0.1/" <<< ${thisYaml})
        url_uhttpd=$(urlencode "${thisUrl}")
        fullName=${thisYaml##*/}
        onlyName=(${fullName//./ })
      # clashConfigNames[$j]=${onlyName}

        # https://stackoverflow.com/questions/525872/echo-tab-characters-in-bash-script
        echo -e "config config_subscribe"      >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption sub_ua 'clash.meta'" >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption sub_convert '0'"     >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption enabled '1'"         >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption name '${onlyName}'"  >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "\toption address 'http://127.0.0.1:25511/sub?target=clash&config=ACL4SSR_Online_Full_AdblockPlus.ini&emoji=true&list=false&udp=true&tfo=true&scv=true&fdn=true&enable_filter=true&filter_script=function%20filter%28N%29%7Bif%28N.Type%3D%3D%3D0%29%7Breturn%20true%3B%7Dlet%20M%3DN.EncryptMethod%3Bif%28M%3D%3D%3Dnull%7C%7CM.length%3D%3D%3D0%29%7Bif%28N.Type%3D%3D%3D1%29%7Breturn%20true%3B%7Dreturn%20false%3B%7Dlet%20C%3D%5B%27aes-128-cfb%27%2C%27aes-128-ctr%27%2C%27aes-128-gcm%27%2C%27aes-192-cfb%27%2C%27aes-192-ctr%27%2C%27aes-192-gcm%27%2C%27aes-256-cfb%27%2C%27aes-256-ctr%27%2C%27aes-256-gcm%27%2C%27auto%27%2C%27chacha20%27%2C%27chacha20-ietf%27%2C%27chacha20-ietf-poly1305%27%2C%27rc4-md5%27%2C%27xchacha20%27%2C%27xchacha20-ietf-poly1305%27%5D%3Blet%20m%3DM.toLowerCase%28%29%3Bfor%28let%20i%3D0%3Bi%3CC.length%3Bi%2B%2B%29%7Bif%28m%3D%3D%3DC%5Bi%5D%29%7Breturn%20false%3B%7D%7Dreturn%20true%3B%7D&exclude=%28CN%7CHK%7CHong%20Kong%7CHongKong%7Cv2cross%7CHONG%20KONG%7CHONGKONG%7CV2CROSS%7CHongkong%7C%E5%BB%A3%E6%9D%B1%7C%E5%8C%97%E4%BA%AC%7C%E5%B9%BF%E4%B8%9C%7C%E8%B4%B5%E5%B7%9E%7C%E4%B8%8A%E6%B5%B7%7C%E9%A6%99%E6%B8%AF%7C%E7%A7%BB%E5%8B%95%7C%E7%A7%BB%E5%8A%A8%7C%E4%B8%AD%E5%9C%8B%7C%E4%B8%AD%E5%9B%BD%7C%E8%B2%B4%E5%B7%9E%7C%E5%85%8D%E8%B4%B9VPN%7C%E8%AE%A2%E9%98%85%E9%9A%8F%E6%97%B6%E4%BC%9A%E5%A4%B1%E6%95%88%7C%E6%97%A5%E6%9C%9F%7C%E7%94%B5%E6%8A%A5%E7%BE%A4%29&url=${url_uhttpd}'" >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
        echo -e "" >> "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"
    done
fi

echo 55555555555555555555555555555555555555555555555555555555555555555555555555
#******************************************************************************
readarray -t arrSubscri < <(cat "/etc/openclash/ClashNodeSubcri.urls")
subsSize=${#arrSubscri[@]}
if (( subsSize > 0 )); then
    for (( j=0; j<${subsSize}; j++ )); do
        subscri=${arrSubscri[$j]}
        arrSplit=(${subscri//,/ })
        relativeFPath=${arrSplit[1]}
        fullName=${relativeFPath##*/}
        onlyName=(${fullName//./ })
        clashConfigNames[$j]=${onlyName}
    done
fi

echo 66666666666666666666666666666666666666666666666666666666666666666666666666
#******************************************************************************
# "/etc/openclash/ClashNodeSubcri.etc_config_openclash.3of4"
optNameSize=${#clashConfigNames[@]}
if (( 0 < optNameSize )); then
    final1=${clashConfigNames[0]}
    if (( 1 < ${#clashConfigNames[@]} )); then
        final1=$(combine_openclash_config "1" "${clashConfigNames[@]}")
    fi
fi

echo 77777777777777777777777777777777777777777777777777777777777777777777777777
echo -e "\toption config_path '/etc/openclash/config/${final1}.yaml'" > "/etc/openclash/ClashNodeSubcri.etc_config_openclash.3of4"

#******************************************************************************
# "/etc/openclash/ClashNodeSubcri.cfg"
cat "/etc/openclash/ClashNodeSubcri.etc_config_openclash.1of4"       >  "/etc/openclash/ClashNodeSubcri.cfg"
cat "/etc/openclash/ClashNodeSubcri.etc_config_openclash.2of4.const" >> "/etc/openclash/ClashNodeSubcri.cfg"
cat "/etc/openclash/ClashNodeSubcri.etc_config_openclash.3of4"       >> "/etc/openclash/ClashNodeSubcri.cfg"
cat "/etc/openclash/ClashNodeSubcri.etc_config_openclash.4of4.const" >> "/etc/openclash/ClashNodeSubcri.cfg"

#******************************************************************************
# "/etc/config/openclash"
mv -f "/etc/config/openclash" "/etc/config/openclash.$(date +%Y%m%d_%H%M%S)"
cp -f "/etc/openclash/ClashNodeSubcri.cfg" "/etc/config/openclash"

echo 88888888888888888888888888888888888888888888888888888888888888888888888888
#******************************************************************************
# restart openclash
if [ $? -eq 0 ]; then
    # "/etc/init.d/openclash" restart;
    /usr/share/openclash/openclash.sh > /dev/null 2>&1
fi

#******************************************************************************
echo -e "\tEnd: $(date +%Y%m%d_%H%M%S)" | tee -a "/etc/openclash/ClashNodeSubcri.log"

echo 99999999999999999999999999999999999999999999999999999999999999999999999999



###############################################################################
######################### Delete too many configuration backup files  #########
###############################################################################
#useWildcardsForPathsContainingSpaces="/tmp/tmp 2/openclash.2"
useWildcardsForPathsContainingSpaces="/etc/config/openclash.2"
# https://stackoverflow.com/questions/6897190/problem-listing-files-in-bash-with-spaces-in-directory-path?rq=3
useWildcardsForPathsContainingSpacesEscaped=`echo "$useWildcardsForPathsContainingSpaces" | sed 's/[[:space:]]/\[[:space:]]/g'`
readarray -t arrOpenclashConfigBakup < <(ls -tc -1 ${useWildcardsForPathsContainingSpacesEscaped}*)
n=${#useWildcardsForPathsContainingSpaces}  # Number of characters to compare
bakSize=${#arrOpenclashConfigBakup[@]}
for (( j=10; j<${bakSize}; j++ )); do
    thisOldConfig=${arrOpenclashConfigBakup[$j]}
    # https://www.google.com/search?q=bash+string+compare+n+characters&pws=0&gl=us&gws_rd=cr
    substring="${thisOldConfig:0:n}"
    if [[ "${substring}" == "${useWildcardsForPathsContainingSpaces}" ]]; then
        rm "${arrOpenclashConfigBakup[$j]}"
    fi
done




echo aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
###############################################################################
######################### Program Singleton quit ##############################
###############################################################################
clean_up

echo bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
exit 0





###############################################################################
################################## END ########################################
###############################################################################

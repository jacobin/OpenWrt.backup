#!/bin/bash

###############################################################################
## 置函数于脚本文件的末尾 #####################################################
###############################################################################
# https://unix.stackexchange.com/questions/724122/is-there-a-way-to-put-helper-functions-at-the-end-of-a-script-file#:~:text=Another%20way%20to%20do%20this,entire%20bash%20script%20in%20functions?
source <(sed '1,/^# HELPER FUNCTIONS #$/d' "$0")

###############################################################################
###############################################################################
###############################################################################
               mybasename=$(basename ${0%\.*})
                      url="https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/refs/heads/master/accelerated-domains.china.conf"
PreviousOne_china_domains="/etc/openclash/custom/pre1_dnsmasq_chinadomain_list.conf"
    dnsmasq_china_domains="/tmp/1.${mybasename}.dnsmasq_chinadomain_list.conf"
  openclash_china_domains="/tmp/2.${mybasename}.oc_chinadomain_list.txt"
    combile_china_domains="/tmp/3.${mybasename}.combile_chinadomain_list.txt"
deduplicate_china_domains="/tmp/4.${mybasename}.deduplicate_chinadomain_list.txt"

wget --no-check-certificate --dns-timeout=10 --connect-timeout=10 --read-timeout=30 --tries=2 "${url}" -O"${dnsmasq_china_domains}"
if ! [[ $? -eq 0 && -f "${dnsmasq_china_domains}" ]]; then
    echo download \"${url}\" failed.
    exit 1
fi

if [[ -f "${PreviousOne_china_domains}" ]]; then
    oldHash=$(sha256sum "${PreviousOne_china_domains}" 2>/dev/null | awk '{print $1}')
    newHash=$(sha256sum "${dnsmasq_china_domains}" 2>/dev/null | awk '{print $1}')
    if [[ "$newHash" == "$oldHash" ]]; then
        echo The file content has not changed. exit here.
        rm -f "${dnsmasq_china_domains}"
        exit 1
    fi
fi

cp -f "${dnsmasq_china_domains}" "${PreviousOne_china_domains}"

nTotalLine=$(wc -l < "${dnsmasq_china_domains}")
iProgress=1

while IFS= read -r line; do
    dns=$(
            IFS='=\/' read i1 i2 i3 i4 <<< ${line}
            echo i3
          # awk '{
          #     n=split($0, a, /[=\/]/);
          #     print a[3]
          # }' <<< "$line"
        )
    echo $dns

    sProgress=$(genProgressString "${iProgress}" "${nTotalLine}")
    >&2 echo -ne "${sProgress}\r"
    let "iProgress++"
done < "${dnsmasq_china_domains}" > "${openclash_china_domains}"
echo

if ! [[ -f "/etc/openclash/custom/openclash_custom_domain_dns.list" ]]; then touch "/etc/openclash/custom/openclash_custom_domain_dns.list"; fi
cat "${openclash_china_domains}" "/etc/openclash/custom/openclash_custom_domain_dns.list" > "${combile_china_domains}"
sort -u "${combile_china_domains}" > "${deduplicate_china_domains}"
mv -f "${deduplicate_china_domains}" "/etc/openclash/custom/openclash_custom_domain_dns.list"
rm -f     "${dnsmasq_china_domains}"
rm -f   "${openclash_china_domains}"
rm -f     "${combile_china_domains}"

exit 0
# HELPER FUNCTIONS #


###############################################################################
######################### function: genProgressString##########################
###############################################################################
function genProgressString {
    progress=$1
    total=$2

  # percent=$(echo "${progress} ${total}" | awk '{printf "%d\n", $1/$2*80+0.5}')
    percent=$[progress*100/total]
    percent_show="(${percent}%)"
    percent_show_len=${#percent_show}

    scale=$[80-5]
    percentScale=$[percent*scale/100]

    space80='                                                                                '
     hash80='################################################################################'
    progress_bar=${hash80:0:${percentScale}}
    empty_space=${space80:0:$[scale-percentScale]}
    wholeshow="${progress_bar}${empty_space}"
    echo "${wholeshow:0:$[80-percent_show_len]}${percent_show}"
}


###############################################################################
################################## File END ###################################
###############################################################################

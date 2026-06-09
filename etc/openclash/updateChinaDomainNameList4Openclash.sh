#!/bin/bash

mybasename=$(basename ${0%\.*})
                      url="https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/refs/heads/master/accelerated-domains.china.conf"
    dnsmasq_china_domains="/tmp/1.${mybasename}.dnsmasq_chinadomain_list.conf"
  openclash_china_domains="/tmp/2.${mybasename}.oc_chinadomain_list.txt"
    combile_china_domains="/tmp/3.${mybasename}.combile_chinadomain_list.txt"
deduplicate_china_domains="/tmp/4.${mybasename}.deduplicate_chinadomain_list.txt"

wget --no-check-certificate --dns-timeout=10 --connect-timeout=10 --read-timeout=30 --tries=2 "${url}" -O"${dnsmasq_china_domains}" > /dev/null 2>&1
if ! [[ $? -eq 0 && -f "${dnsmasq_china_domains}" ]]; then
    echo download \"${url}\" failed.
    exit 1
fi

while IFS= read -r line; do
    dns=$(
            awk '{
                n=split($0, a, /[=\/]/);
                print a[3]
            }' <<< "$line"
        )
    echo $dns
done < "${dnsmasq_china_domains}" > "${openclash_china_domains}"

cat "${openclash_china_domains}" "/etc/openclash/custom/openclash_custom_domain_dns.list" > "${combile_china_domains}"
sort -u "${combile_china_domains}" > "${deduplicate_china_domains}"
mv -f "${deduplicate_china_domains}" "/etc/openclash/custom/openclash_custom_domain_dns.list"

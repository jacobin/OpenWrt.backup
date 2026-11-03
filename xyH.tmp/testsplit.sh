#!/bin/bash

url="https://raw.githubusercontent.com/felixonmars/dnsmasq-china-list/refs/heads/master/accelerated-domains.china.conf"
wget_out_fpath="/tmp/accelerated-domains.china.conf"
wget --no-check-certificate --dns-timeout=10 --connect-timeout=10 --read-timeout=30 --tries=2 "${url}" -O"${wget_out_fpath}"
if ! [[ $? -eq 0 && -f "${wget_out_fpath}" ]]; then
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
done < "${wget_out_fpath}"

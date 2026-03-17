#!/bin/bash

#iptables
#    /etc/init.d/dnsmasq stop
#    /etc/init.d/openclash stop
#    opkg update
#    opkg install bash iptables dnsmasq-full curl ca-bundle ipset ip-full iptables-mod-tproxy iptables-mod-extra ruby ruby-yaml kmod-tun kmod-inet-diag unzip luci-compat luci luci-base
#    opkg install "./luci-app-openclash_0.47.015_all.ipk"

depends=("bash" "iptables" "dnsmasq-full" "curl" "ca-bundle" "ipset" "ip-full" "iptables-mod-tproxy" "iptables-mod-extra" "ruby" "ruby-yaml" "kmod-tun" "kmod-inet-diag" "unzip" "luci-compat" "luci" "luci-base")
for depend in "${depends[@]}"; do
    opkg install ${depend} --force-depends >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "failed: ${depend}"
    fi
done

opkg install "./luci-app-openclash_0.47.015_all.ipk" --force-depends >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "failed: \"./luci-app-openclash_0.47.015_all.ipk\""
    exit 1
fi

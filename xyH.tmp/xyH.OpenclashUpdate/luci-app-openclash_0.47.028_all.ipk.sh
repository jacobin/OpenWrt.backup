#!/bin/bash

target="./luci-app-openclash_0.47.028_all.ipk"

if [ ! -f "${target}" ]; then
    echo "File \"${target}\" does not exist."
    exit 1
fi

# https://github.com/vernesong/OpenClash/releases
#   #iptables
#       opkg update
#       opkg install bash iptables dnsmasq-full curl ca-bundle ipset ip-full iptables-mod-tproxy iptables-mod-extra ruby ruby-yaml kmod-tun kmod-inet-diag unzip luci-compat luci luci-base
#       opkg install /tmp/openclash.ipk

opkg update
depends=("bash" "iptables" "dnsmasq-full" "curl" "ca-bundle" "ipset" "ip-full" "iptables-mod-tproxy" "iptables-mod-extra" "ruby" "ruby-yaml" "kmod-tun" "kmod-inet-diag" "unzip" "luci-compat" "luci" "luci-base")
for depend in "${depends[@]}"; do
    opkg install ${depend} --force-depends >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Failed: ${depend}"
    fi
done

# "/etc/init.d/dnsmasq" stop
"/etc/init.d/openclash" stop
opkg remove "luci-app-openclash"
opkg install "${target}" --force-depends >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Failed: \"${target}\""
    exit 1
fi

#!/bin/bash

target="./luci-app-openclash_0.47.075_all.ipk"

if [ ! -f "${target}" ]; then
    echo "File \"${target}\" does not exist."
    exit 1
fi

opkg update

echo 11111111111111111111111

# "/etc/init.d/dnsmasq" stop
"/etc/init.d/openclash" stop

echo 22222222222222222222222
# https://github.com/vernesong/OpenClash/releases
#   #iptables
#       opkg update
#       opkg install bash iptables dnsmasq-full curl ca-bundle ipset ip-full iptables-mod-tproxy iptables-mod-extra ruby ruby-yaml kmod-tun kmod-inet-diag unzip luci-compat luci luci-base
#       opkg install /tmp/openclash.ipk
depends=("bash" "iptables" "dnsmasq-full" "curl" "ca-bundle" "ipset" "ip-full" "iptables-mod-tproxy" "iptables-mod-extra" "ruby" "ruby-yaml" "kmod-tun" "kmod-inet-diag" "unzip" "luci-compat" "luci" "luci-base")
for depend in "${depends[@]}"; do
    opkg install ${depend} --force-depends >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Failed: ${depend}"
    else
        echo "Success: ${depend}"
    fi
done
echo 33333333333333333333333

opkg remove "luci-app-openclash"
echo 44444444444444444444444

opkg install "${target}" --force-depends >/dev/null 2>&1
echo 55555555555555555555555

if [ $? -ne 0 ]; then
    echo "Failed: \"${target}\""
    exit 1
fi

echo 66666666666666666666666

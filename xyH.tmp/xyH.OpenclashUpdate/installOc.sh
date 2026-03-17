#!/bin/bash

#iptables
#   opkg update
#   opkg --force-depends install bash iptables dnsmasq-full curl ca-bundle ipset ip-full iptables-mod-tproxy iptables-mod-extra ruby ruby-yaml kmod-tun kmod-inet-diag unzip luci-compat luci luci-base
#   opkg --force-depends --force-downgrade install "./luci-app-openclash_0.46.086_all.ipk"

# 2025-08-03
echo "" | tee installOc.log
date | tee installOc.log
/etc/init.d/openclash stop | tee installOc.log
opkg update | tee installOc.log
opkg --force-depends install bash iptables dnsmasq-full curl ca-bundle ipset ip-full iptables-mod-tproxy iptables-mod-extra ruby ruby-yaml kmod-tun kmod-inet-diag unzip luci-compat luci luci-base | tee installOc.log
opkg --force-depends install "./luci-app-openclash_0.46.137_all.ipk" | tee installOc.log
# shutdown -r now | tee installOc.log

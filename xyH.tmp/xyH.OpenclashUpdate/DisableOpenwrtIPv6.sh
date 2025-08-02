#!/bin/bash

uci set dhcp.@dnsmasq[0].filter_aaaa='1'
    read -rp $'Are you sure you want to continue? (Y/n) : ' -ei $'Y' key;
uci commit dhcp
    read -rp $'Are you sure you want to continue? (Y/n) : ' -ei $'Y' key;
/etc/init.d/odhcpd disable
    read -rp $'Are you sure you want to continue? (Y/n) : ' -ei $'Y' key;
echo 'net.ipv6.conf.all.disable_ipv6 = 1' >> /etc/sysctl.conf
    read -rp $'Are you sure you want to continue? (Y/n) : ' -ei $'Y' key;
sysctl -p /etc/sysctl.conf

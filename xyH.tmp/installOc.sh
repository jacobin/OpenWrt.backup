#iptables
opkg update
opkg --force-depends install bash iptables dnsmasq-full curl ca-bundle ipset ip-full iptables-mod-tproxy iptables-mod-extra ruby ruby-yaml kmod-tun kmod-inet-diag unzip luci-compat luci luci-base
opkg --force-depends --force-downgrade install ./luci-app-openclash_0.46.086_all.ipk

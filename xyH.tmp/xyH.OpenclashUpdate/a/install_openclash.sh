#!/bin/bash
if ! test -f "./luci-app-openclash_0.46.064_all.ipk"; then echo "Main file \"./luci-app-openclash_0.46.064_all.ipk\" NOT exist."; exit 1; fi

# https://adao.me/OpenClash-an-zhuang-he-jian-dan-shi-yong-jiao-cheng-ji-chang-jian-cuo-wu-jie-jue-openwrt2021-yue-12-yue-6-ri-?p=404&locale=zh
rm -f /var/lock/opkg.lock

opkg update

# https://blog.hellowood.dev/posts/openwrt-%E5%AE%89%E8%A3%85%E4%BD%BF%E7%94%A8-openclash/
## OpenClash 依赖的是 dnsmasq-full，所以需要移除默认的dnsmasq，否则会导致 OpenClash 安装失败
opkg remove "dnsmasq" && opkg install "dnsmasq-full"

# https://blog.hellowood.dev/posts/openwrt-%E5%AE%89%E8%A3%85%E4%BD%BF%E7%94%A8-openclash/
# https://github.com/vernesong/OpenClash
opkg install "dnsmasq-full"        --force-depends && if [ $? -ne 0 ]; then echo "failed: dnsmasq-full"       ; fi
opkg install "coreutils"           --force-depends && if [ $? -ne 0 ]; then echo "failed: coreutils"          ; fi
opkg install "coreutils-nohup"     --force-depends && if [ $? -ne 0 ]; then echo "failed: coreutils-nohup"    ; fi
opkg install "bash"                --force-depends && if [ $? -ne 0 ]; then echo "failed: bash"               ; fi
opkg install "curl"                --force-depends && if [ $? -ne 0 ]; then echo "failed: curl"               ; fi
opkg install "ca-certificates"     --force-depends && if [ $? -ne 0 ]; then echo "failed: ca-certificates"    ; fi
opkg install "ipset"               --force-depends && if [ $? -ne 0 ]; then echo "failed: ipset"              ; fi
opkg install "ip-full"             --force-depends && if [ $? -ne 0 ]; then echo "failed: ip-full"            ; fi
opkg install "libcap"              --force-depends && if [ $? -ne 0 ]; then echo "failed: libcap"             ; fi
opkg install "libcap-bin"          --force-depends && if [ $? -ne 0 ]; then echo "failed: libcap-bin"         ; fi
opkg install "ruby"                --force-depends && if [ $? -ne 0 ]; then echo "failed: ruby"               ; fi
opkg install "ruby-yaml"           --force-depends && if [ $? -ne 0 ]; then echo "failed: ruby-yaml"          ; fi
opkg install "unzip"               --force-depends && if [ $? -ne 0 ]; then echo "failed: unzip"              ; fi
opkg install "iptables"            --force-depends && if [ $? -ne 0 ]; then echo "failed: iptables"           ; fi
opkg install "kmod-ipt-nat"        --force-depends && if [ $? -ne 0 ]; then echo "failed: kmod-ipt-nat"       ; fi
opkg install "iptables-mod-tproxy" --force-depends && if [ $? -ne 0 ]; then echo "failed: iptables-mod-tproxy"; fi
opkg install "iptables-mod-extra"  --force-depends && if [ $? -ne 0 ]; then echo "failed: iptables-mod-extra" ; fi
opkg install "ip6tables-mod-nat"   --force-depends && if [ $? -ne 0 ]; then echo "failed: ip6tables-mod-nat"  ; fi

# https://adao.me/OpenClash-an-zhuang-he-jian-dan-shi-yong-jiao-cheng-ji-chang-jian-cuo-wu-jie-jue-openwrt2021-yue-12-yue-6-ri-?p=404&locale=zh
opkg install "kmod-tun"            --force-depends && if [ $? -ne 0 ]; then echo "failed: kmod-tun"           ; fi
opkg install "kmod-inet-diag"      --force-depends && if [ $? -ne 0 ]; then echo "failed: kmod-inet-diag"     ; fi
opkg install "kmod-nft-tproxy"     --force-depends && if [ $? -ne 0 ]; then echo "failed: kmod-nft-tproxy"    ; fi

opkg install "luci"                --force-depends && if [ $? -ne 0 ]; then echo "failed: luci"               ; fi
opkg install "luci-base"           --force-depends && if [ $? -ne 0 ]; then echo "failed: luci-base"          ; fi
opkg install "luci-compat"         --force-depends && if [ $? -ne 0 ]; then echo "failed: luci-compat"        ; fi

opkg install "./luci-app-openclash_0.46.064_all.ipk" --force-depends && if [ $? -ne 0 ]; then echo "failed: \"./luci-app-openclash_0.46.064_all.ipk\"" ; fi

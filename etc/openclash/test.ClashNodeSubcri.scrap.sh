###############################################################################
###############################################################################
# Post-processing procedure
#        grep -v '^\#' "/www/Hxy/openclash/barry-far/barry-far-vmess.txt"   >  "/www/Hxy/openclash/barry-far/barry-far-vmess.txt.tmp2"
#        grep -v '^\#' "/www/Hxy/openclash/barry-far/barry-far-vless.txt"   >  "/www/Hxy/openclash/barry-far/barry-far-vless.txt.tmp2"
#        grep -v '^\#' "/www/Hxy/openclash/barry-far/barry-far-trojan.txt"  >  "/www/Hxy/openclash/barry-far/barry-far-trojan.txt.tmp2"
#        grep -v '^\#' "/www/Hxy/openclash/barry-far/barry-far-ss.txt"      >  "/www/Hxy/openclash/barry-far/barry-far-ss.txt.tmp2"
#        grep -v '^\#' "/www/Hxy/openclash/barry-far/barry-far-ssr.txt"     >  "/www/Hxy/openclash/barry-far/barry-far-ssr.txt.tmp2"
#
#        mv -f "/www/Hxy/openclash/barry-far/barry-far-vmess.txt.tmp2"   "/www/Hxy/openclash/barry-far/barry-far-vmess.txt2"
#        mv -f "/www/Hxy/openclash/barry-far/barry-far-vless.txt.tmp2"   "/www/Hxy/openclash/barry-far/barry-far-vless.txt2"
#        mv -f "/www/Hxy/openclash/barry-far/barry-far-trojan.txt.tmp2"  "/www/Hxy/openclash/barry-far/barry-far-trojan.txt2"
#        mv -f "/www/Hxy/openclash/barry-far/barry-far-ss.txt.tmp2"      "/www/Hxy/openclash/barry-far/barry-far-ss.txt2"
#        mv -f "/www/Hxy/openclash/barry-far/barry-far-ssr.txt.tmp2"     "/www/Hxy/openclash/barry-far/barry-far-ssr.txt2"
base64  -w0 "/www/Hxy/openclash/barry-far/barry-far-vmess.txt"  > "/www/Hxy/openclash/barry-far/barry-far-vmess.txt3"
base64  -w0 "/www/Hxy/openclash/barry-far/barry-far-vless.txt"  > "/www/Hxy/openclash/barry-far/barry-far-vless.txt3"
base64  -w0 "/www/Hxy/openclash/barry-far/barry-far-trojan.txt" > "/www/Hxy/openclash/barry-far/barry-far-trojan.txt3"
base64  -w0 "/www/Hxy/openclash/barry-far/barry-far-ss.txt"     > "/www/Hxy/openclash/barry-far/barry-far-ss.txt3"
base64  -w0 "/www/Hxy/openclash/barry-far/barry-far-ssr.txt"    > "/www/Hxy/openclash/barry-far/barry-far-ssr.txt3"

wget "http://127.0.0.1:25511/sub?target=clash"\
"&config=ACL4SSR_Online_Full_AdblockPlus.ini"\
"&append_type=true"\
"&emoji=true"\
"&list=false"\
"&udp=true"\
"&tfo=true"\
"&scv=true"\
"&fdn=true"\
"&url=http%3A%2F%2F127.0.0.1%2FHxy%2Fopenclash%2Fbarry-far%2Fbarry-far-All_Configs_base64_Sub.txt" \
-O"/www/Hxy/openclash/barry-far/barry-far-All_Configs_base64_Sub.yaml.tmp"

cat "/www/Hxy/openclash/barry-far/barry-far-All_Configs_base64_Sub.yaml.tmp" | grep -v "x11" | grep -v -iF "Hysteria2" > "/www/Hxy/openclash/barry-far/barry-far-All_Configs_base64_Sub.yaml"

rm -f "/www/Hxy/openclash/barry-far/barry-far-All_Configs_base64_Sub.yaml.tmp"

date >> /etc/openclash/ClashNodeSubcri.log

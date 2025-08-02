# Openclash --> 全局设置 --> GEO 数据库订阅 --> 自定义
curl -v https://fastly.jsdelivr.net/gh/alecthw/mmdb_china_ip_list@release/lite/Country.mmdb -o /etc/openclash/GeoSite.dat
curl -v https://fastly.jsdelivr.net/gh/alecthw/mmdb_china_ip_list@release/Country.mmdb -o /etc/openclash/Country.mmdbs


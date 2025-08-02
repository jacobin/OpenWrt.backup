#!/bin/bash

A=barry-far-All_Configs_base64_Sub
echo 'http://127.0.0.1:25511/sub?target=clash'\
'&config=ACL4SSR_Online_Full_AdblockPlus.ini'\
'&append_type=true'\
'&emoji=true'\
'&list=false'\
'&udp=true'\
'&tfo=true'\
'&scv=true'\
'&fdn=true'\
'&url=http%3A%2F%2F127.0.0.1%2FHxy%2Fopenclash%2F$A.txt' -O"$A.yaml.tmp"


A=barry-far-All_Configs_base64_Sub
echo "http://127.0.0.1:25511/sub?target=clash"\
"&config=ACL4SSR_Online_Full_AdblockPlus.ini"\
"&append_type=true"\
"&emoji=true"\
"&list=false"\
"&udp=true"\
"&tfo=true"\
"&scv=true"\
"&fdn=true"\
"&url=http%3A%2F%2F127.0.0.1%2FHxy%2Fopenclash%2F$A.txt" -O"$A.yaml.tmp"


A="barry-far-All_Configs_base64_Sub"
echo $A

#!/bin/bash

# ARRAY=" \
# http://openwrt.org \
# http://wiki.openwrt.org \
# "
# i=1
#
# for j in $ARRAY
# do
#     echo $i: $j
#     i=`expr $i + 1`
# done

# input='host-name:port,host-name2:port2,One,XX X,192.178.88:999,17.0.0'
# echo "input: $input"
#
# OLDIFS=$IFS;IFS=,
# for token in $input; do
#     hostname=$(echo ${token%:*})
#     port=$(echo ${token#*:})
#     echo "hostname: $hostname, port: $port"
# done
# IFS=$OLDIFS

awk '{$1=$1;print}'
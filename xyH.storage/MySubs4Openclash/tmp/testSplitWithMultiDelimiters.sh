#!/bin/bash

#awk '{
#  n=split($0, a, /[\/@:?=&#]/);
#  for (i=1; i<=n; i++) {
#    print a[i];
#  }
#}' <<< "trojan://y8DvPRQfz@163.177.46.183:28113?allowInsecure=1&peer=download.windowsupdate.com#IEPL+%C2%B7+%E6%97%A5%E6%9C%ACJP+%C2%B7+23+%C2%B7+%E6%B7%B1%E6%B8%AFIEPL"

input_string="trojan://y8DvPRQfz@163.177.46.183:28113?allowInsecure=1&peer=download.windowsupdate.com#IEPL+%C2%B7+%E6%97%A5%E6%9C%ACJP+%C2%B7+23+%C2%B7+%E6%B7%B1%E6%B8%AFIEPL"
# Save the current IFS value
old_ifs="$IFS"
# Set IFS to ';,'
IFS='/@:?=&#'
# Read the string into an array
read -ra elements <<< "$input_string"
# Restore the old IFS value
IFS="$old_ifs"

# Loop through the elements
for i in "${!elements[@]}"; do
#for element in "${elements[@]}"; do
    printf "%s\t%s\n" "$i" "${elements[$i]}"
done
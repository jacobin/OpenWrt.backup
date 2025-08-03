#!/bin/bash

# https://www.baeldung.com/linux/shell-get-url-from-string#:~:text=s%2F.%2A%20%28http%20%5Bs%5D%3F%3A%2F%2F%20%20%20%5D%2B%29.%2A%2F1%2Fp%26%5D%20defines%20a,sed%20to%20locate%20and%20extract%20the%20complete%20URL

# echo Welcome to our website "<p>https://nodefree.org/dy/2024/05/20240524.txt</p>" | grep -o 'http[s]\?://[^ ]\+' | head -1
#
# echo Welcome to our website "<p>https://nodefree.org/dy/2024/05/20240524.txt</p>" | \
#   awk '{
#     for (i = 1; i <= NF; i++) {
#       if ($i ~ /^http[s]?:\/\/[^\ ]+$/) {
#         print $i
#         break
#       }
#     }
#   }'

#  echo Welcome to our website "<p>https://nodefree.org/dy/2024/05/20240524.txt</p>" | sed -n 's/.*\(http[s]\?:\/\/[^ ]\+\).*/\1/p'

#  echo Welcome to our website "<p>https://nodefree.org/dy/2024/05/20240524.txt</p>" | grep -o '<a .*href=.*>' | sed -e 's/<a /\n<a /g' | sed -e 's/<a .*href=['"'"'"]//' -e 's/["'"'"'].*$//' -e '/^$/ d'

# echo Welcome to our website "<p>https://nodefree.org/dy/2024/05/20240524.txt</p>" |  grep 'URL' | rev | cut -d "'" -f 2 | rev
# echo Welcome to our website "<p>https://nodefree.org/dy/2024/05/20240524.txt</p>" |  grep 'URL' | cut -d "'" -f 4 | sed s/'http:\/\/'/''/g

# output='Array { Dict { Name = afp://or-fs-001/vol1 URL = afp://or-fs-001/vol1 } Dict { Name = smb://or-fs-001/vol1 URL = smb://or-fs-001/vol1 } Dict { Name = vnc://or-fs-001/vol1 URL = vnc://or-fs-001/vol1 } Dict { Name = ftp://or-fs-001/vol1 URL = ftp://or-fs-001/vol1 } }'
#
# count=$(echo "$output" | grep -o 'Name =' | wc -l)
# names=($(grep -o 'Name = [^ ]\+' <<< "$output" | cut -f3- -d' '))
# echo $count = ${#names[@]}
# for name in "${names[@]}" ; do
#     echo "$name"
# done

# # https://stackoverflow.com/questions/16623835/remove-a-fixed-prefix-suffix-from-a-string-in-bash
# prefix="hell"
# suffix="ld"
# string="hello-world"
# foo=${string#"$prefix"}
# foo=${foo%"$suffix"}
# echo "${foo}"

function digString() {
    resultVar="$1"
    local string="$2"
    local prefix="$3"
    local suffix="$4"
    local foo=${string#"$prefix"}
    foo=${foo%"$suffix"}
    eval ${resultVar}=${foo}
}

set ret=
digString "ret" "1234567890" "12" "890"
echo $ret

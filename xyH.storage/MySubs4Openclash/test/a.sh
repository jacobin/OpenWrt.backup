#!/bin/bash
## https://www.cyberciti.biz/faq/extract-bash-get-filename-extension/
input_file_name="/home/vivek/Pictures/night.T.png"
echo "${input_file_name%.*}"
echo "${input_file_name##*.}"

## https://www.cyberciti.biz/faq/bash-get-basename-of-filename-or-directory-name/
FILE="/home/vivek/lighttpd.tar.gz"
basename "$FILE"
f="$(basename -- $FILE)"
echo "$f"

echo "$(basename -- $0)"

echo "+++++++++++++++++++++++++++++++"
input_file_name="$0"
echo "${input_file_name%.*}"
echo "${input_file_name##*.}"

## https://www.cyberciti.biz/faq/bash-get-basename-of-filename-or-directory-name/
FILE="$0"
basename "$FILE"
f="$(basename -- $FILE)"
echo "$f"

echo "$(basename -- $0)"

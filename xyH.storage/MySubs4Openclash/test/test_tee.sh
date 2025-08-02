#!/bin/bash

## https://www.cnblogs.com/sparkdev/p/10006970.html
#MyString=abcABC123ABCabc
#echo ${MyString:3}       # ABC123ABCabc，注意：此时索引是从 0 开始的。
#echo ${MyString:1:5}     # bcABC
#
#echo +++${*:2}+++ # 打印出第 2 个和后边所有的位置参数。
#echo +++${@:2}+++ # 同上。
#echo +++${*:2:3}+++ # 从第 2 个开始, 连续打印 3 个位置参数。
#exit 1
#

# https://stackoverflow.com/questions/692000/how-do-i-write-standard-error-to-a-file-while-using-tee-with-a-pipe/692407#692407
# https://unix.stackexchange.com/questions/352107/generic-way-to-get-temp-path
TMPDIR="/xyH.storage/MySubs4Openclash/test"
out="${TMPDIR:-/tmp}/out.$$" err="${TMPDIR:-/tmp}/err.$$"
mkfifo "$out" "$err"
trap 'rm "$out" "$err"' EXIT
tee -a stdout.log < "$out" &
tee -a stderr.log < "$err" >&2 &
wget www.youtube.com -Oytb.html >"$out" 2>"$err"

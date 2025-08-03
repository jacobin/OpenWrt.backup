#!/bin/sh
## https://stackoverflow.com/questions/34532677/how-to-assign-the-result-of-echo-to-a-variable-in-bash-script
## https://stackoverflow.com/questions/918886/how-do-i-split-a-string-on-a-delimiter-in-bash?page=1&tab=scoredesc#tab-top
IN="bla@some.com;john@home.com"
ADD1=$(echo $IN | cut -d \; -f 1)
ADD2=$(echo $IN | cut -d \; -f 2)
echo $ADD1
echo $ADD2
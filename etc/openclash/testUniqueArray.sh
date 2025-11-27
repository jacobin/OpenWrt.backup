#!/bin/bash

#declare -a ip_addrs=(192.168.1.101 192.168.1.105 192.168.1.105 192.168.1.106)
#declare -A uniq_tmp
#for ip in "${ip_addrs[@]}"; do
#    echo $ip++++
#   uniq_tmp[$ip]=99
#done
#echo "unique: ${!uniq_tmp[@]}"
#

#ip_addrs=(192.168.1.101 192.168.1.105 192.168.1.105 192.168.1.106)
#uniqs_arr=($(for ip in "${ip_addrs[@]}"; do echo "$ip"; done | sort -u))
#echo "unique: ${uniqs_arr[@]}"

#ip_addrs=(192.168.1.101 192.168.1.105 192.168.1.105 192.168.1.106)
#sorted_ips=($(for ip in "${ip_addrs[@]}"; do echo "$ip"; done | sort))
#unique_ips=($(echo "${sorted_ips[@]}" | tr ' ' '\n' | uniq))
#echo "unique: ${unique_ips[@]}"




#
################################################################################
### 程序流程图 #################################################################
################################################################################
## https://zhuanlan.zhihu.com/p/54494213
#<< EOF
#    original
#        --> pass_openclash_subscription
#            --> etc_config_openclash.mutable("PLACEHOLDER_ACTIVE_OPENCLASH_CONFIG_PATH")
#                --> /etc/config/openclash
#EOF
#
## https://stackoverflow.com/questions/43158140/way-to-create-multiline-comments-in-bash
#: '
#    original
#        --> pass_openclash_subscription
#            --> etc_config_openclash.mutable("PLACEHOLDER_ACTIVE_OPENCLASH_CONFIG_PATH")
#                --> /etc/config/openclash
#'
#
#echo ++++++++++++++++++++++++++


#
##!/bin/bash
#
#my_array=( "apple" "banana" "orange" "apple" "grape" "banana" )
#
#echo "Original array:"
#printf "%s\n" "${my_array[@]}"
#
#echo -e "\nDuplicate elements:"
#printf "%s\n" "${my_array[@]}" | sort | uniq -d
#
#echo -e "\nElements with counts (duplicates have count > 1):"
#printf "%s\n" "${my_array[@]}" | sort | uniq -c


##!/bin/bash
#
#my_array=(apple banana orange apple grape banana)
#
## Convert array to newline-separated string and sort uniquely
#unique_elements=($(printf "%s\n" "${my_array[@]}" | sort -u))
#
## Check if the number of unique elements is less than the original array's length
#if (( ${#unique_elements[@]} < ${#my_array[@]} )); then
#    echo "The array contains duplicates."
#else
#    echo "The array does not contain duplicates."
#fi


##!/bin/bash
#
#declare -a original_array=("apple" "banana" "apple" "orange" "banana")
#declare -A unique_elements
#
#for element in "${original_array[@]}"; do
#    unique_elements["$element"]=1
#done
#
## The unique elements are now the keys of the associative array
#echo "Unique elements: ${!unique_elements[@]}"
#


##!/bin/bash
#
## Define your array with duplicate values
#my_array=(apple banana orange apple grape banana kiwi apple)
#
## Print each element on a new line, sort them, and then find duplicates
#printf "%s\n" "${my_array[@]}" | sort | uniq -d

#!/bin/bash


#
## Function to simulate an assertion
#assert_true() {
#  local condition="$1"
#  local message="${2:-Assertion failed!}"
#
#  if ! eval "$condition"; then
#    echo "ERROR: $message" >&2
#    exit 1
#  fi
#}
#
## Example usage:
#VALUE=10
#assert_true "[ $VALUE -eq 10 ]" "Value is not 10"
#
#ANOTHER_VALUE=5
#assert_true "[ $ANOTHER_VALUE -gt 10 ]" "Another value is not greater than 10" # This will fail




#
#
## Function to simulate an assertion
#assert_true() {
#  local condition="$1"
#  local message="${2:-Assertion failed!}"
#
#  if ! eval "$condition"; then
#    echo -e "\tERROR: $message" >&2
#    exit 1
#  fi
#}
#
## Example usage:
#VALUE=9
#assert_true "[ $VALUE -eq 10 ]" "Value is not 10\n\tEnd: $(date +%Y%m%d_%H%M%S)"


#
#
##!/bin/bash
#
#string1="Hello"
#string2="hello"
#
## Convert both to lowercase for comparison
#if [[ "${string1,,}" == "${string2,,}" ]]; then
#  echo "Strings are equal (case-insensitive)."
#else
#  echo "Strings are not equal."
#fi
#
## Convert both to uppercase for comparison (alternative)
#if [[ "${string1^^}" == "${string2^^}" ]]; then
#  echo "Strings are equal (case-insensitive)."
#else
#  echo "Strings are not equal."
#fi

#
#
#my_string="   Hello World!   "
#trimmed_string=$(echo "$my_string" | xargs)
#echo "$trimmed_string"



#URL="http://127.0.0.1:25511"
#
## Get the HTTP status code
#STATUS_CODE=$(curl --output /dev/null --silent --head --write-out "%{http_code}" "$URL")
#echo $STATUS_CODE
#
## Check the status code
#if (( STATUS_CODE == 200 )); then
#  echo "URL is up! (Status Code: $STATUS_CODE)"
#else
#  echo "URL is down or returned an error. (Status Code: $STATUS_CODE)"
#fi


#if timeout 2s curl -v telnet://"www.google.com":80 2>&1 | grep "Connected to"; then
#    echo connnnnnn
#else
#    echo notconnnnnn
#fi

#
#    curl -v --connect-timeout 2 telnet://"127.0.0.1":25511
#    if [[ $? -eq 0 ]]; then
#        echo "'${element}' connected"
#    else
#        echo "Connection with ${element} failed."
#    fi


#while read "127.0.0.1" 25511; do
#    r=$(bash -c 'exec 3<> /dev/tcp/'$host'/'$port';echo $?' 2>/dev/null)
#    if [ "$r" = "0" ]; then
#         echo "$host $port is open"
#    else
#         echo "$host $port is closed"
#         exit 1 # To force fail result in ShellScript
#    fi
#done



#
#
#         host=127.0.0.1
#         port=25588
#
#         r=$(bash -c 'exec 3<> /dev/tcp/127.0.01/25511;echo $?' 2>/dev/null)
#         if [ "$r" = "0" ]; then
#              echo "$host $port is open"
#         else
#              echo "$host $port is closed"
#         fi
#
# host=127.0.0.1
# port=25522
#
# r=$(bash -c 'exec 3<> /dev/tcp/127.0.01/25522;echo $?' 2>/dev/null)
# if [ "$r" = "0" ]; then
#      echo "$host $port is open"
# else
#      echo "$host $port is closed"
# fi
#
#     host=127.0.0.1
#     port=25511
#
#     r=$(bash -c 'exec 3<> /dev/tcp/127.0.01/25588;echo $?' 2>/dev/null)
#     if [ "$r" = "0" ]; then
#          echo "$host $port is open"
#     else
#          echo "$host $port is closed"
#     fi



#cat << EOF | tee output.txt
#This is the first line.
#This is the second line.
#And this is the third line.
#EOF



#my_array=(element0 element1 element2)
#echo "${my_array[0]}" # Prints "element0"
#
#subsSize=${#my_array[@]}
#for (( j=0; j<${subsSize}; j++ )); do
#    echo ${my_array[${j}]}
#done
#




#
##!/bin/bash
#
#my_string=" item1 ,    item  2 , item3 "
#
## Save the original IFS
#OLD_IFS=$IFS
#
## Set IFS to a comma
#IFS=','
#
## Read the string into an array, splitting by comma
#read -ra items <<< "$my_string"
#
## Restore the original IFS
#IFS=$OLD_IFS
#
## Print the resulting array elements (for demonstration)
#for item in "${items[@]}"; do
#    echo "Item: \"$item\""
#done
#
## Process the array elements, trimming whitespace
#for i in "${!items[@]}"; do
#    # Remove leading and trailing whitespace
#    items[$i]=$(echo "${items[$i]}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
#done
#
## Print the resulting array elements (for demonstration)
#for item in "${items[@]}"; do
#    echo "Item: \"$item\""
#done
#



#
##!/bin/bash
#
## Example input with spaces within elements
#input_data="first element    with spaces
#second element also with spaces
#third"
#
## Read each line into an array
#readarray -t my_array <<< "$input_data"
#
## Print the array elements
#for i in "${!my_array[@]}"; do
#  echo "Element $i: ${my_array[$i]}"
#done

#
##!/bin/bash
#
## Create a sample file
#echo "This is line one" > file.txt
#echo "  This is line two with leading spaces" >> file.txt
#echo "This is line three with trailing spaces  " >> file.txt
#echo "This is line four with   multiple   spaces" >> file.txt
#
## Preserve the original IFS
#OLD_IFS="$IFS"
#
## Set IFS to only newline
#IFS=$'\n'
#
## Read the file into an array, ignoring spaces as delimiters
#readarray -t my_array < file.txt
#
## Restore the original IFS
#IFS="$OLD_IFS"
#
## Print the array elements
#echo "Array elements:"
#for element in "${my_array[@]}"; do
#  echo "-> \"$element\""
#done

#
#
##! /bin/bash
#
## path to the file
#filepath="/etc/passwd"
#
## storing file size in a variable.
#size=$(wc -c < $filepath)
#
## displaying file size
#echo "The size of file is $size Bytes"


##!/bin/bash
#
## Function to simulate an assert
#assert() {
#  local condition="$1"
#  local message="$2"
#
#  if ! eval "$condition"; then
#    echo "Assertion failed: $message" | tee -a aaa.txt
#    exit 1
#  fi
#}
#
## Example usage:
#echo "Running tests..."
#
## Test 1: Assert equality of numbers
#num1=10
#num2=10
#assert "[ $num1 -ne $num2 ]" "Numbers are equal ($num1 vs $num2)"
#
## Test 2: Assert a string contains a substring
#my_string="Hello World"
#assert "[[ \"$my_string\" == *\"World\"* ]]" "String does not contain 'World'"
#
## Test 3: Assert a file exists (example of a potential failure)
## assert "[ -f /path/to/nonexistent_file.txt ]" "File does not exist"
#
#echo "All assertions passed."


#
## https://stackoverflow.com/questions/16391208/print-a-files-last-modified-date-in-bash
#start_time=$(date -r "/etc/config/minidlna" +%s%3N) # Get start time in milliseconds since epoch
## ... your commands to be timed ...
#end_time=$(date +%s%3N)   # Get end time in milliseconds since epoch
#duration_ms=$((end_time - start_time))
#echo "Execution time in ms: $duration_ms"


#aaa=4
#bbb=5
#
#if [ ${aaa} < 0 ]; then
#    echo aaaaaaaaaaaaaaaaaaaaaa
#fi
#
#if [ ${aaa} <= 0 ]; then
#    echo aaaaaaaaaaaaaaaaaaaaaa
#fi
#
#
#if [[ ${aaa} < 0 ]]; then
#    echo aaaaaaaaaaaaaaaaaaaaaa
#fi
#
#if [[ ${aaa} <= 0 ]]; then
#    echo aaaaaaaaaaaaaaaaaaaaaa
#fi
#
#if (( aaa < 0 )); then
#    echo aaaaaaaaaaaaaaaaaaaaaa
#fi
#
#if (( aaa <= 0 )); then
#    echo aaaaaaaaaaaaaaaaaaaaaa
#fi
#



###############################################################################
## 如果连内网都已宕机，那么就取消此次的订阅 #####################################
###############################################################################
readarray -t arrSpeedTestResult < <( wget -p -O/dev/null "http://www.baidu.com" --dns-timeout=10 --connect-timeout=10 --read-timeout=10 --tries=1 2>&1 | grep -o "[0-9.]\\+ [KM]*B/s" )
speedSize=${#arrSpeedTestResult[@]}
if (( speedSize <= 0 )); then
    echo ${speedSize}aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    exit 1
fi
echo ${speedSize}
unset arrSpeedTestResult; unset speedSize

###############################################################################
## 如果外网尚且可用，那么就取消此次的订阅 #####################################
###############################################################################
readarray -t arrSpeedTestResult < <( wget -p -O/dev/null "http://www.youtube.com" --dns-timeout=10 --connect-timeout=10 --read-timeout=10 --tries=1 2>&1 | grep -o "[0-9.]\\+ [KM]*B/s" )
speedSize=${#arrSpeedTestResult[@]}
if [[ 0 < ${speedSize} ]]; then
    echo ${speedSize}bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
    exit 1
fi
echo ${speedSize}
unset arrSpeedTestResult; unset speedSize


#!/bin/bash


###############################################################################
######################### function: singleton_clean_up ########################
###############################################################################
function singleton_clean_up() {
    timeEnd=$(date +%s%3N)
    total_seconds=$((timeEnd-TIMEBEGIN))
    seconds=$((total_seconds % 60))
    minutes=$(((total_seconds / 60) % 60))
    hours=$((total_seconds / 3600))
    printf -v formatted_string "%02d:%02d:%02d" $hours $minutes $seconds
    exit "$1"
}

###############################################################################
######################### function: assert_true ###############################
###############################################################################
function assert_true() {
    local condition="$1"
    local message="${2:-Assertion failed!}"

    if ! eval "$condition"; then
        echo "ERROR: ${message}"
        singleton_clean_up 1
    fi
}

###############################################################################
######################### function: LeapYear ##################################
###############################################################################
# https://blog.csdn.net/Stars____/article/details/106972527
function LeapYear() {
    year=$1
    if ( (( year%4==0 )) && (( year%100!=0 )) ) || (( year%400==0 )); then
        return 0 # true
    fi
    return 1 # false
}

###############################################################################
######################### function: MonthDays #################################
###############################################################################
function MonthDays() {
    year=$(expr $1 + 0) # 02 ==> 2
    month=$(expr $2 + 0)
    Days=( 29 31 28 31 30 31 30 31 31 30 31 30 31 )

    if (( 2==$month )) && LeapYear $year; then
        month=0;
    fi

    echo ${Days[$month]}
}


###############################################################################
######################### function: isdigit ###################################
###############################################################################
# https://stackoverflow.com/questions/806906/how-do-i-test-if-a-variable-is-a-number-in-bash
function isdigit() {
    str=$1
    if [[ ! $str =~ ^[0-9]+$ ]]; then
        return 1
    fi
    return 0
}


###############################################################################
######################### function: is_valid_datetime #########################
###############################################################################
# https://blog.csdn.net/weixin_45956148/article/details/107862145
function is_valid_datetime() { # 20260123_102345
    Date=$1

    if [ ${#Date} -ne 15 ];then
        return 1
    fi

  #       YYYYMMDD=$(echo $Date |cut -c 1-8)
  # CONNECTED_CHAR=$(echo $Date |cut -c 9-9)
  #         hhmmss=$(echo $Date |cut -c 10-15)
          YYYYMMDD=${Date:0:8 }
    CONNECTED_CHAR=${Date:8:1 }
            hhmmss=${Date:9:6 }

    if [ ! $CONNECTED_CHAR=="_" ];then
        return 1
    fi

    if ! isdigit $YYYYMMDD; then
        return 1
    fi

    if ! isdigit $hhmmss; then
        return 1
    fi

 #    Year=$(echo $Date |cut -c 1-4)
 #   Month=$(echo $Date |cut -c 5-6)
 #     Day=$(echo $Date |cut -c 7-8)
 #    hour=$(echo $Date |cut -c 10-11)
 #  minute=$(echo $Date |cut -c 12-13)
 #  second=$(echo $Date |cut -c 14-15)
      Year=${Date:0:4}
     Month=${Date:4:2}
       Day=${Date:6:2}
      hour=${Date:9:2}
    minute=${Date:11:2}
    second=${Date:13:2}

    if [ ${#YYYYMMDD} -ne 8 ];then
        return 1
    fi

    if [ ${#hhmmss} -ne 6 ];then
        return 1
    fi

    # Numbers like "08" and "09" are treated as octal by bash.
  #   Year=$(expr $Year   + 0)
  #  Month=$(expr $Month  + 0)
  #    Day=$(expr $Day    + 0)
  #   hour=$(expr $hour   + 0)
  # minute=$(expr $minute + 0)
  # second=$(expr $second + 0)
      Year=$((10#$Year))
     Month=$((10#$Month))
       Day=$((10#$Day))
      hour=$((10#$hour))
    minute=$((10#$minute))
    second=$((10#$second))



    if ! { [ $Month -gt 0 -a $Month -le 12 ]; }; then
        return 1
    fi

    Days=$(MonthDays $Year $Month)
    if (( $Day <= 0 )) || (( $Days < $Day )); then
        return 1
    fi

    if (( $hour < 0 )) || (( 23 < $hour )); then
        return 1
    fi

    if (( $minute < 0 )) || (( 59 < $minute )); then
        return 1
    fi

    if (( $second < 0 )) || (( 59 < $second )); then
        return 1
    fi

    return 0
}
# # Example Usage:
# function Testcase() {
#     if is_valid_datetime "$1"; then
#         echo "'$1' is a valid date."
#     else
#         echo "'$1' is not a valid date."
#     fi
# }
#
# Testcase "20240228_120342"
# Testcase "20240231_120342"
# Testcase "20240232_120342"


###############################################################################
################## function: trans2datetimestring #############################
###############################################################################
function trans2datetimestring() {
    local s="$1"
    local sDatetime="${s:0:4}-${s:4:2}-${s:6:2} ${s:9:2}:${s:11:2}:${s:13:2}"
    echo ${sDatetime}
}


###############################################################################
################# function: ArrayIntersect ####################################
###############################################################################
# https://www.google.com/search?q=bash+function+trans+2+array+as+param
# https://stackoverflow.com/questions/7870230/array-intersection-in-bash
# https://stackoverflow.com/questions/10582763/how-to-return-an-array-in-bash-without-using-globals
function ArrayIntersect() {
    local -n array1=$1
    local -n array2=$2
    local -n result=$3                    # use nameref for indirection
    result=()

    l2=" ${array2[*]} "                   # add framing blanks
    for item in ${array1[@]}; do
        if [[ $l2 =~ " $item " ]] ; then  # use $item as regexp
            result+=($item)
        fi
    done
}


###############################################################################
############################ Link404Over7 #####################################
###############################################################################
function Link404Over7() {
    local -n arrResult=$1

    tarFPath="/etc/openclash/loop6.bak/ClashNodeSubcri.loop6"
    if [ -f "${tarFPath}.tar.gz" ]; then
        gzip -d "${tarFPath}.tar.gz" &> /dev/null
        assert_true "[ ! -f \"${tarFPath}.tar.gz\" ]" "Failed to unzip file \"${tarFPath}.tar.gz\"."
        tar x -v -f "${tarFPath}.tar" -C "/" >/dev/null 2>&1
        assert_true "[ -f \"${tarFPath}.tar\" ]" "tar's behavior towards file \"${tarFPath}.tar\" does not meet expectations."
        rm -f "${tarFPath}.tar" &> /dev/null
        assert_true "[ ! -f \"${tarFPath}.tar\" ]" "Delete file \"${tarFPath}.tar\" failed."
    fi

    # arrLoop6datetime, arrLoop6fpath
    declare -a arrLoop6datetime
    readarray -t arrLoop6fpath < <( ls -t -r -1 /etc/openclash/loop6.bak/*.2???????_?????? )
    bakSize=${#arrLoop6fpath[@]}
    for (( j=0; j<bakSize; j++ )); do
        fpath=${arrLoop6fpath[j]}
        fpathLen=${#fpath}
        assert_true "(( 15 < fpathLen ))" "The list of filenames for naturalization is incorrect."
        last15chars=${fpath: -15}
        assert_true "is_valid_datetime \"${last15chars}\"" "The last fifteen characters of the filename must be a date expression."
        datetime=$(trans2datetimestring "${last15chars}")
        nDatetime=$(date -d "${datetime}" +%s)
        let arrLoop6datetime[j]=nDatetime
    done

    # n7daysago
    nNow=$( date '+%s' )
    nTodayYYYYmmdd=$( date -d "$( date '+%F' )" +%s )
    let n7daysago=$(( nNow - (6*24*60*60) - (nNow-nTodayYYYYmmdd) ))

    # arr7Loop6datetime, arr7Loop6fpath
    declare -a arr7Loop6datetime
    declare -a arr7Loop6fpath
    for (( j=0, k=0; j<bakSize; j++ )); do
        if (( n7daysago < ${arrLoop6datetime[j]} )); then
            arr7Loop6datetime[k]=${arrLoop6datetime[j]}
            arr7Loop6fpath[k]=${arrLoop6fpath[j]}
            ((k++))
        fi
    done

    bak7size=${#arr7Loop6fpath[@]}
    if (( bak7size < 7 )); then
        return 1
    fi

    # bucket7
    declare -a bucket7
    for (( j=0; j<bak7size; j++ )); do
        let bucketIdx=$(( ( arr7Loop6datetime[j] - n7daysago ) / (24*60*60) ))
        if (( 0 <= bucketIdx )); then
            bucket7[ bucketIdx ]+=${arr7Loop6fpath[j]}
            bucket7[ bucketIdx ]+="|"
        fi
    done

    bucket7size=${#bucket7[@]}
    if (( bucket7size < 7 )); then
        return 1
    fi

    assert_true "(( 7 == bucket7size ))" "The number of buckets $bucket7size should be equal to 7."

    # There are only 7 buckets, and each bucket contains one or more file paths similar to "/etc/openclash/loop6.bak/ClashNodeSubcri.loop6.20260826_212751", with each path separated by a '|'.
    # arrLoop6Urls0
    declare -a arrLoop6Urls0
    {
        declare -a arrLoop6FPathsPerDay
        arrLoop6FPathsPerDay=(${bucket7[0]//|/ })
        nThisBucketSize=${#arrLoop6FPathsPerDay[@]}
        readarray -t arrLoop6Urls0 < ${arrLoop6FPathsPerDay[0]}
        for (( k=1; k<nThisBucketSize; k++ )); do
            readarray -t arrLoop6UrlsK < ${arrLoop6FPathsPerDay[k]}
            ArrayIntersect arrLoop6Urls0 arrLoop6UrlsK arrLoop6UrlsIntersetResult
            arrLoop6Urls0=("${arrLoop6UrlsIntersetResult[@]}")
        done
    }
    for (( j=1; j<bucket7size; j++ )); do
        declare -a arrLoop6FPathsPerDay
        arrLoop6FPathsPerDay=(${bucket7[j]//|/ })
        nThisBucketSize=${#arrLoop6FPathsPerDay[@]}
        readarray -t arrLoop6Urls00 < ${arrLoop6FPathsPerDay[0]}
        for (( k=1; k<nThisBucketSize; k++ )); do
            readarray -t arrLoop6UrlsK < ${arrLoop6FPathsPerDay[k]}
            ArrayIntersect arrLoop6Urls00 arrLoop6UrlsK arrLoop6UrlsIntersetResult
            arrLoop6Urls00=("${arrLoop6UrlsIntersetResult[@]}")
        done
        ArrayIntersect arrLoop6Urls0 arrLoop6Urls00 arrLoop6UrlsIntersetResult
        arrLoop6Urls0=("${arrLoop6UrlsIntersetResult[@]}")
    done

    arrResult=("${arrLoop6Urls0[@]}")
}

###############################################################################
############################ Link0sizeOver7 ###################################
###############################################################################
function Link0sizeOver7() {
    local -n arrResult=$1

    # arr0sizerec_sorted
    size0fpath="/etc/openclash/ClashNodeSubcri.0size"
    readarray -t arr0sizerec < ${size0fpath}
    readarray -td '' arr0sizerec_sorted < <(printf '%s\0' "${arr0sizerec[@]}" | sort -z -n)
    bakSize=${#arr0sizerec_sorted[@]}

    # arrUrl, arrDatetime
    declare -a arrDatetime
    declare -a arrUrl
    for (( j=0; j<bakSize; j++ )); do
        let Len=${#arr0sizerec_sorted}
        assert_true "(( 20 < Len ))" "This record is too short; it doesn't seem like a legitimate record."
        arrUrl[j]=${arr0sizerec_sorted[j]: 16 }
        sDatetime=${arr0sizerec_sorted[j]: 0: 15 }
        assert_true "is_valid_datetime \"${sDatetime}\"" "The first fifteen characters of the recorded text are not a valid timestamp."
        datetime=$(trans2datetimestring "${sDatetime}")
        nDatetime=$(date -d "${datetime}" +%s)
        let arrDatetime[j]=nDatetime
    done

    # n7daysago
    nNow=$( date '+%s' )
    nTodayYYYYmmdd=$( date -d "$( date '+%F' )" +%s )
    let n7daysago=$(( nNow - (6*24*60*60) - (nNow-nTodayYYYYmmdd) ))

    # arr7datetime, arr7url
    declare -a arr7datetime
    declare -a arr7url
    for (( j=0, k=0; j<bakSize; j++ )); do
        if (( n7daysago < ${arrDatetime[j]} )); then
            arr7datetime[k]=${arrDatetime[j]}
            arr7url[k]=${arrUrl[j]}
            ((k++))
        fi
    done

    bak7size=${#arr7url[@]}
    if (( bak7size < 7 )); then
        return 1
    fi

    # bucket7
    declare -a bucket7
    for (( j=0; j<bak7size; j++ )); do
        let bucketIdx=$(( ( arr7datetime[j] - n7daysago ) / (24*60*60) ))
        if (( 0 <= bucketIdx )); then
            bucket7[ bucketIdx ]+=${arr7url[j]}
            bucket7[ bucketIdx ]+="|"
        fi
    done

    bucket7size=${#bucket7[@]}
    if (( bucket7size < 7 )); then
        return 1
    fi

    assert_true "(( 7 == bucket7size ))" "The number of buckets $bucket7size should be equal to 7."

    # There are only 7 buckets, and each bucket contains one or more urls, with each url separated by a '|'.
    # arrUrls0
    declare -a arrUrls0
    arrUrls0=(${bucket7[0]//|/ })
    for (( k=1; k<bucket7size; k++ )); do
        declare -a arrUrlsK
        arrUrlsK=(${bucket7[k]//|/ })
        ArrayIntersect arrUrls0 arrUrlsK arrUrlsIntersetResult
        arrUrls0=("${arrUrlsIntersetResult[@]}")
    done

    arrResult=("${arrUrls0[@]}")

}


###############################################################################
################################ table27 ######################################
###############################################################################
function table27() {
    local size0fpath=$1
    local -n arr7result=$2

    # arr0sizerec_sorted_unique
    readarray -t arr0sizerec < ${size0fpath}
    readarray -t arr0sizerec_sorted_unique < <(printf "%s\n" "${arr0sizerec[@]}" | sort -u)
    bakSize=${#arr0sizerec_sorted_unique[@]}

    # arrUrl, arrDatetime
    declare -a arrDatetime
    declare -a arrUrl
    for (( j=0; j<bakSize; j++ )); do
        let Len=${#arr0sizerec_sorted_unique[j]}
        assert_true "(( 20 < Len ))" "This record is too short; it doesn't seem like a legitimate record."
        sDatetime=${arr0sizerec_sorted_unique[j]: 0: 15 }
        arrUrl[j]=${arr0sizerec_sorted_unique[j]: 16 }
        assert_true "is_valid_datetime \"${sDatetime}\"" "The first 15 characters of the recorded text are not a valid timestamp."
        sStdDatetime=$(trans2datetimestring "${sDatetime}")
        nDatetime=$(date -d "${sStdDatetime}" +%s)
        let arrDatetime[j]=nDatetime
    done

    # n7daysago
    nNow=$( date '+%s' )
    nTodayYYYYmmdd=$( date -d "$( date '+%F' )" +%s )
    let n7daysago=$(( nNow - (6*24*60*60) - (nNow-nTodayYYYYmmdd) ))

    # arr7datetime, arr7url
    declare -a arr7datetime
    declare -a arr7url
    for (( j=0, k=0; j<bakSize; j++ )); do
        if (( n7daysago < ${arrDatetime[j]} )); then
            arr7datetime[k]=${arrDatetime[j]}
            arr7url[k]=${arrUrl[j]}
            ((k++))
        fi
    done

    bak7size=${#arr7url[@]}
    if (( bak7size < 7 )); then
        return 1
    fi

    # bucket7
    declare -a bucket7
    for (( j=0; j<bak7size; j++ )); do
        let bucketIdx=$(( ( arr7datetime[j] - n7daysago ) / (24*60*60) ))
        if (( 0 <= bucketIdx )); then
            bucket7[ bucketIdx ]+=${arr7url[j]}
            bucket7[ bucketIdx ]+="|"
        fi
    done

    bucket7size=${#bucket7[@]}
    if (( bucket7size < 7 )); then
        return 1
    fi

    assert_true "(( 7 == bucket7size ))" "The number of buckets $bucket7size should be equal to 7."

    # There are only 7 buckets, and each bucket contains one or more urls, with each url separated by a '|'.
    # arrUrls0
    declare -a arrUrls0
    arrUrls0=(${bucket7[0]//|/ })
    for (( k=1; k<bucket7size; k++ )); do
        declare -a arrUrlsK
        arrUrlsK=( ${bucket7[k]//|/ })
        ArrayIntersect arrUrls0 arrUrlsK arrUrlsIntersetResult
        arrUrls0=("${arrUrlsIntersetResult[@]}")
    done

    arr7result=("${arrUrls0[@]}")
}


###############################################################################
############################ file2table #######################################
###############################################################################
function file2table() {
    local tarFPath=$1
    local tableResult=$2
    [ -f "${tableResult}" ] || touch "${tableResult}"
    assert_true "[ -f \"${tableResult}\" ]" "There cannot be a file at that location \"${tableResult}\"."
  # archFolder=$(dirname "$tarFPath")

    if [ -f "${tarFPath}.tar.gz" ]; then
        gzip -d "${tarFPath}.tar.gz" &> /dev/null
        assert_true "[ ! -f \"${tarFPath}.tar.gz\" ]" "Failed to unzip file \"${tarFPath}.tar.gz\"."
        tar x -v -f "${tarFPath}.tar" -C "/" >/dev/null 2>&1
        assert_true "[ -f \"${tarFPath}.tar\" ]" "tar's behavior towards file \"${tarFPath}.tar\" does not meet expectations."
        rm -f "${tarFPath}.tar" &> /dev/null
        assert_true "[ ! -f \"${tarFPath}.tar\" ]" "Delete file \"${tarFPath}.tar\" failed."
    fi

    # arrLoop6fpath
    readarray -t arrLoop6fpath < <( ls -t -r -1 ${tarFPath}.2???????_?????? )
    bakSize=${#arrLoop6fpath[@]}
    for (( j=0; j<bakSize; j++ )); do
        fpath=${arrLoop6fpath[j]}
        fpathLen=${#fpath}
        assert_true "(( 15 < fpathLen ))" "The list of filenames for naturalization is incorrect."
        last15chars=${fpath: -15}
        assert_true "is_valid_datetime \"${last15chars}\"" "The last fifteen characters of the filename must be a date expression."
        readarray -t arrLoop6Urls < ${fpath}
        for p in "${arrLoop6Urls[@]}"; do
            IFS=',' read -r -a tmpArr <<< "$p"
            echo "${last15chars} ${tmpArr[0]}" >> "${tableResult}"
        done
    done
}

# 1111
# Link404Over7 result
# printf '%s\n' "${result[@]}"

# 2222
# table27 "/etc/openclash/ClashNodeSubcri.0size" result
# printf '%s\n' "${result[@]}"

# 3333
date +%Y%m%d_%H%M%S
rm -f "/tmp/aaatttmmmppp.txt"
file2table "/etc/openclash/loop6.bak/ClashNodeSubcri.loop6" "/tmp/aaatttmmmppp.txt"
table27 "/tmp/aaatttmmmppp.txt" result3
printf '%s\n' "${result3[@]}"
date +%Y%m%d_%H%M%S
# table27 "/etc/openclash/ClashNodeSubcri.oldsubs" result
# printf '%s\n' "${result[@]}"

# trans2datetimestring "20260731_132228" datetime
# echo $datetime


# file2table "/etc/openclash/loop6.bak/ClashNodeSubcri.loop6" "/tmp/aaabcccccccccccbbbbbbb.txt"

exit 0


        printf '%s\n' "${arrLoop6PerDay[@]}"




#   aaaa   function tee_echo() {
#   aaaa       echo -e $(date "+%Y-%m-%d %H:%M:%S $1")
#   aaaa   }
#   aaaa
#   aaaa   ###############################################################################
#   aaaa   ######################### function: singleton_clean_up ########################
#   aaaa   ###############################################################################
#   aaaa   function singleton_clean_up() {
#   aaaa       timeEnd=$(date +%s%3N)
#   aaaa       total_seconds=$((timeEnd-TIMEBEGIN))
#   aaaa       seconds=$((total_seconds % 60))
#   aaaa       minutes=$(((total_seconds / 60) % 60))
#   aaaa       hours=$((total_seconds / 3600))
#   aaaa       printf -v formatted_string "%02d:%02d:%02d" $hours $minutes $seconds
#   aaaa       exit "$1"
#   aaaa   }
#   aaaa
#   aaaa   ###############################################################################
#   aaaa   ######################### function: assert_true ###############################
#   aaaa   ###############################################################################
#   aaaa   function assert_true() {
#   aaaa       local condition="$1"
#   aaaa       local message="${2:-Assertion failed!}"
#   aaaa
#   aaaa       if ! eval "$condition"; then
#   aaaa           tee_echo "\tERROR: ${message}\n"
#   aaaa           singleton_clean_up 1
#   aaaa       fi
#   aaaa   }
#   aaaa   # Example usage:
#   aaaa   VALUE=10
#   aaaa   assert_true "[ $VALUE -eq 10 ]" "Value is not 10"
#   aaaa   echo 111111111111111111111111111111
#   aaaa   ANOTHER_VALUE=5
#   aaaa   assert_true "[ $ANOTHER_VALUE -gt 10 ]" "Another value is not greater than 10" # This will fail
#   aaaa   echo 222222222222222222222222222222

################################## END ########################################

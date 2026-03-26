#!/bin/bash


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

    YYYYMMDD=$(echo $Date |cut -c 1-8)
    CONNECTED_CHAR=$(echo $Date |cut -c 9-1)
    hhmmss=$(echo $Date |cut -c 10-15)

    if [ ! $CONNECTED_CHAR=="_" ];then
        return 1
    fi

    if ! isdigit $YYYYMMDD; then
        return 1
    fi

    if ! isdigit $hhmmss; then
        return 1
    fi

      Year=$(echo $Date |cut -c 1-4)
     Month=$(echo $Date |cut -c 5-6)
       Day=$(echo $Date |cut -c 7-8)
      hour=$(echo $Date |cut -c 10-11)
    minute=$(echo $Date |cut -c 12-13)
    second=$(echo $Date |cut -c 14-15)

    if [ ${#YYYYMMDD} -ne 8 ];then
        return 1
    fi

    if [ ${#hhmmss} -ne 6 ];then
        return 1
    fi

      Year=$(expr $Year   + 0)
     Month=$(expr $Month  + 0)
       Day=$(expr $Day    + 0)
      hour=$(expr $hour   + 0)
    minute=$(expr $minute + 0)
    second=$(expr $second + 0)


    if ! { [ $Month -gt 0 -a $Month -le 12 ]; }; then
        return 1
    fi

    Days=$(MonthDays $Year $Month)
    if (( Day <= 0 )) || (( Days < Day )); then
        return 1
    fi

    if (( hour < 0 )) || (( 23 < hour )); then
        return 1
    fi

    if (( minute < 0 )) || (( 59 < minute )); then
        return 1
    fi

    if (( second < 0 )) || (( 59 < second )); then
        return 1
    fi

    return 0
}

###############################################################################
######################### function: is_valid_datetime #########################
###############################################################################
if is_valid_datetime $1; then
    echo "日期合法"
else
    echo "日期不合法"
fi

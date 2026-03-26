#!/bin/bash
[ -f /etc/init.d/functions ] && source /etc/init.d/functions || echo "函数库文件不存在！"
read -p "请输入一个纯8位数字组成的日期：" Date
if [[ ! $Date =~ ^[0-9]+$ ]];then
    echo "日期不合法！"
    exit
fi
if [ ${#Date} -ne 8 ];then
    echo "日期不合法！"
    exit
fi
Year=$(echo $Date |cut -c 1-4)
Month=$(echo $Date |cut -c 5-6)
Day=$(echo $Date |cut -c 7-8)
if [ $Month -eq 1 ];then
    if [ $Day -gt 0 -a $Day -le 31 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 2 ];then
    S=$(echo $Date |cut -c 3-4)
    if [ $S -eq 0 ];then
        #世纪年（xx00）需要被400整除才是闰年
        R=$(($Year % 400))
        if [ $R -eq 0 ];then
            if [ $Day -gt 0 -a $Day -le 29 ];then
                echo "日期合法！" /bin/true
            else
                echo "日期不合法！"
            fi
        else
            if [ $Day -gt 0 -a $Day -le 28 ];then
                echo "日期合法！" /bin/true
            else
                echo "日期不合法！"
            fi
        fi
    else
        #非世纪年只要能被4整除就是闰年
        N=$(($Year % 4))
        if [ $N -eq 0 ];then
            if [ $Day -gt 0 -a $Day -le 29 ];then
                echo "日期合法！" /bin/true
            else
                echo "日期不合法！"
            fi
        else
            if [ $Day -gt 0 -a $Day -le 28 ];then
                echo "日期合法！" /bin/true
            else
                echo "日期不合法！"
            fi
        fi
    fi
elif [ $Month -eq 3 ];then
    if [ $Day -gt 0 -a $Day -le 31 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 4 ];then
    if [ $Day -gt 0 -a $Day -le 30 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 5 ];then
    if [ $Day -gt 0 -a $Day -le 31 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 6 ];then
    if [ $Day -gt 0 -a $Day -le 30 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 7 ];then
    if [ $Day -gt 0 -a $Day -le 31 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 08 ];then
    if [ $Day -gt 0 -a $Day -le 31 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 09 ];then
    if [ $Day -gt 0 -a $Day -le 30 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 10 ];then
    if [ $Day -gt 0 -a $Day -le 31 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 11 ];then
    if [ $Day -gt 0 -a $Day -le 30 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
elif [ $Month -eq 12 ];then
    if [ $Day -gt 0 -a $Day -le 31 ];then
        echo "日期合法！" /bin/true
    else
        echo "日期不合法！"
    fi
else
    echo "日期不合法！"
fi
# https://blog.csdn.net/weixin_45956148/article/details/107862145

#!/bin/bash

astring="   lol  "
echo ${astring} | xargs

trimed=$(echo "   lol  " | xargs)
echo ${trimed}

trimed="abc$(echo "   lol  " | xargs)"
echo ${trimed}

trimed=$(echo ${astring} | xargs)
echo ${trimed}

#
str="/some/directory/file"
if [[ ${str:0:1} == "/" ]] ; then echo 1; else echo 0; fi

str=
if [[ ${str:0:1} == "/" ]] ; then echo 1; else echo 0; fi

#
str="/some/directory/file"
if [[ ${str:0:1} != "/" ]] ; then echo 0; else echo 1; fi

#
function aFun {
    local Nproc=5                        # 可同时运行的最大作业数

    # 在fd6中放置$Nproc个空行作为令牌
    local i
    for(( i=1; i<=$Nproc; i++)); do
        echo $i
    done

    }

    aFun

       if [[ -z "${refUrl}" ]] || [[ -z "${outSuburls}" ]] || [[ -z "${threadDatetime}" ]]; then
        echo "aaaaaaaaaaaaaaaaa"
        exit 1
    fi
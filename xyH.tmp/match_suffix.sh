#!/bin/bash

readarray -t allFPaths < <(cat "./allfiles.txt" | grep -v "/overlay/" | grep -v "/proc/" | grep -v "/rom/" | grep -v "/bin/" )
readarray -t allSuffixs < <(cat "./ex.txt")

for thisFPath in ${allFPaths[@]}; do
    for thisSuffix in ${allSuffixs[@]}; do
        case ${thisFPath} in */${thisSuffix}) echo ${thisFPath};; esac
    done
done
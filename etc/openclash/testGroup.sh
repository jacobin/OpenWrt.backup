#!/bin/bash

# arr=(1 2 3 4 5 6 7 8 9 a b c)
# asize=${#arr[@]}
# declare -i groupCount=$(( (asize+4)/5 ))
# echo "asize=${asize}"
# echo "groupCount=${groupCount}"
# for (( i = 0; i < ${groupCount}; i++ )); do
#     begin=$((i*5))
#     tmpa=$((asize-begin))
#     echo -e "\ttmpa=${tmpa}"
#     if (( 5 < asize-begin )); then
#         echo -e "\tfull size"
#         thissize=5
#     else
#         echo -e "\tIncomplete size"
#         thissize=$((asize-begin))
#     fi
#     end=$((begin+thissize))
#     echo -e "\t${begin},${end}"
# done
#


arr=(1 2 3 4 5 6 7 8 9 a b c)
asize=${#arr[@]}
for (( begin = 0; begin < ${asize}; begin+=5 )); do
    end=$((begin+5))
    if (( asize < end )); then end=${asize}; fi
    echo -e "\t${begin},${end}"
done

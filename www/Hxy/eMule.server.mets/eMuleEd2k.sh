#!/bin/bash

##  { wget "https://upd.emule-security.org/server.met"                    -N -O13.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 13.met failed; fi; } &
## #{ wget "http://www.server-met.de/dl.php?load=min&trace=41709915.5556" -N -O12.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 12.met failed; fi; } &
## #{ wget "http://www.server-met.de/dl.php?load=max&trace=41709915.5556" -N -O11.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 11.met failed; fi; } &
##  { wget "http://www.server-met.de/dl.php?load=gz&trace=41709915.5556"  -N -O10.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 10.met failed; fi; } &
##  { wget "http://www.server-met.de/dl.php?load=gz&trace=39956982.7778"  -N -O09.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 09.met failed; fi; } &
##  { wget "http://upd.emule-security.org/server.met"                     -N -O08.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 08.met failed; fi; } &
##  { wget "http://shortypower.org/server.met"                            -N -O07.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 07.met failed; fi; } &
##  { wget "http://gruk.org/server.met"                                   -N -O06.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 06.met failed; fi; } &
##  { wget "http://edk.peerates.net/servers.met"                          -N -O05.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 05.met failed; fi; } &
##  { wget "http://ed2k.iscool.net/5lsb48wb/max/server.met"               -N -O04.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 04.met failed; fi; } &
##  { wget "http://ed2k.2x4u.de/v1s4vbaf/min/server.met"                  -N -O03.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 03.met failed; fi; } &
##  { wget "http://ed2k.2x4u.de/v1s4vbaf/micro/server.met"                -N -O02.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 02.met failed; fi; } &
##  { wget "http://ed2k.2x4u.de/v1s4vbaf/max/server.met"                  -N -O01.met -T5 --no-check-certificate > /dev/null 2>&1; if [ $? -ne 0 ]; then echo 01.met failed; fi; } &

## https://stackoverflow.com/questions/8880603/loop-through-an-array-of-strings-in-bash
## declare an array variable
declare -a array=(
    "https://upd.emule-security.org/server.met"
    "http://www.server-met.de/dl.php?load=min&trace=41709915.5556"
    "http://www.server-met.de/dl.php?load=max&trace=41709915.5556"
    "http://www.server-met.de/dl.php?load=gz&trace=41709915.5556"
    "http://www.server-met.de/dl.php?load=gz&trace=39956982.7778"
    "http://upd.emule-security.org/server.met"
    "http://shortypower.org/server.met"
    "http://gruk.org/server.met"
    "http://edk.peerates.net/servers.met"
    "http://ed2k.iscool.net/5lsb48wb/max/server.met"
    "http://ed2k.2x4u.de/v1s4vbaf/min/server.met"
    "http://ed2k.2x4u.de/v1s4vbaf/micro/server.met"
    "http://ed2k.2x4u.de/v1s4vbaf/max/server.met"
)

# get length of an array
arrayLength=${#array[@]}

# use for loop to read all values and indexes
for (( i=0; i<${arrayLength}; i++ )); do
    ## https://stackoverflow.com/questions/8789729/how-to-zero-pad-a-sequence-of-integers-in-bash-so-that-all-have-the-same-width
    printf -v j "%02d" $i
    {
        wget "${array[$i]}" -N -O"/www/Hxy/eMule.server.mets/${j}.met.tmp" -T2 --no-check-certificate > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo -e "\n${j} -- ${array[$i]} failed."
        else
            mv -f "/www/Hxy/eMule.server.mets/${j}.met.tmp" "/www/Hxy/eMule.server.mets/${j}.met" > /dev/null 2>&1
        fi
    } &
done

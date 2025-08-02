#!/bin/bash

i=0; while read line
do
    filesArray[ i ]="$line"
    filesArray2[ $i ]="$line"
    #echo ${filesArray[i]}
    (( i++ ))
done < <( find "/xyH.storage/MySubs4Openclash/test/test_array_index" -maxdepth 1 -type f )
declare -p filesArray
declare -p filesArray2
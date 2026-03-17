#!/bin/bash

timeNow=`date '+%Y-%m-%d-%H-%M-%S'`
tarFolder="/tmp/openclash_backup_$timeNow"

mkdir "$tarFolder"

res=$? && if test "$res" != "0"; then echo "make directory '$tarFolder' failed."; exit 1; fi

ls -1 "/etc/openclash" > ./openclash_backup_file_list_$timeNow.txt

if ! test -f "./openclash_backup_file_list_$timeNow.txt"; then echo "create file 'openclash_backup_file_list_$timeNow.txt' failed."; exit 1; fi

# https://stackoverflow.com/questions/1521462/looping-through-the-content-of-a-file-in-bash
while IFS="" read -r p || [ -n "$p" ]
do
    #files="$files \"./$p\""
    cp -a "/etc/openclash/$p" "$tarFolder"
    res=$? && if test "$res" != "0"; then echo "copy path '/etc/openclash/$p' failed."; exit 1; fi
done < ./openclash_backup_file_list_$timeNow.txt

    ## https://unix.stackexchange.com/questions/398042/bash-script-to-tar-quoting-issue
    #declare -a files
    #while IFS="" read -r p || [ -n "$p" ]
    #do
    #    files+=("$p")
    #done

    ## https://stackoverflow.com/questions/63857312/in-ash-how-to-set-multiple-line-output-to-variables
    #readarray -t files << "$(cat ./openclash_backup_file_list_$timeNow.txt)"

    # tar -cvzf "./openclash_backup_$timeNow.tgz" "-C/etc/openclash" "$tarFolder"
# https://blog.csdn.net/whatday/article/details/111559926
tar -cvf "./openclash_backup_$timeNow.tgz" "$tarFolder"
tar -rvf "./openclash_backup_$timeNow.tgz" "/etc/config/openclash"
res=$? && if test "$res" != "0"; then echo "tar '$tarFolder' failed."; exit 1; fi

rm -R "$tarFolder"
rm -f "./openclash_backup_file_list_$timeNow.txt"

exit 0

#!/bin/bash

# https://stackoverflow.com/questions/35995670/list-only-file-names-in-directories-and-subdirectories-in-bash
# https://superuser.com/questions/527535/how-do-i-list-files-with-full-paths-in-linux
# https://stackoverflow.com/questions/27340307/list-file-using-ls-command-in-linux-with-full-path
# https://stackoverflow.com/questions/9954680/how-to-store-directory-files-listing-into-an-array
# https://stackoverflow.com/questions/10574794/how-to-list-only-files-and-not-directories-of-a-directory-bash
function afunc() {
     declare -a array
    i=0; while read line
    do
        array[ $i ]="$line"
        echo ${array[i]}
        (( i++ ))
    done < <( find $PWD -maxdepth 1 -type f )
}

afunc
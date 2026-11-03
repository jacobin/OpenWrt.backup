#!/bin/bash

###############################################################################
###############################################################################
###############################################################################
function validate_filename() {
    local -r key=$1
    local -ri len=$(echo "${#key}")

    if [[ $key == "" ]]; then
       return 1
    fi

    if [[ $key == "." ]] || [[ $key == ".." ]]; then
        # "." and ".." are added automatically and always exist, so you can't have a
        # file named . or .. // https://askubuntu.com/a/416508/660555
        return 1
    fi

    if [ $len -gt 255 ]; then
       # String's length check
       return 1
    fi

    if ! [[ $key =~ ^[0-9a-zA-Z._-]+$ ]]; then
        # Checks whether valid characters exist
        return 1
    fi

    local -r _key=$(echo $key | cut -c1-1)
    if ! [[ $_key =~ ^[0-9a-zA-Z.]+$ ]]; then
        # Checks the first character
        return 1
    fi

    return 0
}


###########################

declare -ra arrFilenames=("/.config"
                          "afile.txt"
                          "b#file."
                          "cfile.")

for n in "${arrFilenames[@]}"; do
    if validate_filename "${n}"; then
        echo "${n}" is a valid filename.
    else
        echo "${n}" is NOT a valid filename.
    fi
done

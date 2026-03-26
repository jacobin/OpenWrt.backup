#!/bin/bash

###############################################################################
######################### function: assert_true ###############################
###############################################################################
function assert_true() {
    local condition="$1"
    local message="${2:-Assertion failed!}"

    if ! eval "$condition"; then
        tee_echo "\tERROR: ${message}\n\tEnd: $(date +%Y%m%d_%H%M%S)"
        singleton_clean_up 1
    fi
}
## Example usage:
#VALUE=10
#assert_true "[ $VALUE -eq 10 ]" "Value is not 10"
#
#ANOTHER_VALUE=5
#assert_true "[ $ANOTHER_VALUE -gt 10 ]" "Another value is not greater than 10" # This will fail

###############################################################################
######################### function: is_valid_datetime #########################
###############################################################################
function is_valid_datetime() {
    # OpenWrt uses the busybox-date utility to manage time, supporting formats
    # like YYYY-MM-DD hh:mm[:ss], [YYYY.]MM.DD-hh:mm[:ss],
    # or [[[[[YY]YY]MM]DD]hh]mm[.ss]. The command date -s is used to manually
    # set the system time, while ntpd -q -p is used for syncing via NTP.
    date -D "%Y%m%d_%H%M%S" "$1" > NUL 2>&1
    if [ $? -eq 0 ]; then
        return 0
    fi

    return 1
}
# # Example Usage:
# function Testcase() {
#     if is_valid_datetime "$1"; then
#         echo "'$1' is a valid date."
#     else
#         echo "'$1' is not a valid date."
#     fi
# }
#
# Testcase "20240228_120342"
# Testcase "20240231_120342"
# Testcase "20240232_120342"

###############################################################################
######################### function: tar_old_files #############################
###############################################################################
function tar_old_files() {
    # https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
    tarFPath=$(echo "$1" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    targetFPathMatchingPattern=$(echo "$2" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    nReserve=$(echo "$3" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    folder1="$(dirname "${tarFPath}")"
    folder2="$(dirname "${targetFPathMatchingPattern}")"
    assert_true "[[ ${folder1} == ${folder2} ]]" "\"${folder1}\" and \"${folder2}\" must have the same parent folder"

    # It must be ensured that "tarFPath" is not in the pattern matching of "targetFPathMatchingPattern"

    if [ -f "${tarFPath}.tar.gz" ]; then
        gzip -d "${tarFPath}.tar.gz"
        assert_true "[ ! -f \"${tarFPath}.tar.gz\" ]" "Failed to unzip file \"${tarFPath}.tar.gz\"."
        tar x -v -f "${tarFPath}.tar" -C "/"
        assert_true "[ -f \"${tarFPath}.tar\" ]" "tar's behavior towards file \"${tarFPath}.tar\" does not meet expectations."
        rm "${tarFPath}.tar" -f
        assert_true "[ ! -f \"${tarFPath}.tar\" ]" "Delete file \"${tarFPath}.tar\" failed."
    fi

    ListFPathTemp=$(mktemp "${TMPDIR:-/tmp/}$(basename $0).XXXXXXXXXXXX")
    ls -t -r -1 ${targetFPathMatchingPattern} > ${ListFPathTemp} 2>/dev/null
    ls -t -r -1 ${targetFPathMatchingPattern}.2???????_?????? >> ${ListFPathTemp} 2>/dev/null
    readarray -t arrOpenclashConfigBakup < <(cat "${ListFPathTemp}")
    rm "${ListFPathTemp}" -f
    bakSize=${#arrOpenclashConfigBakup[@]}

    NowDatetime="$(date +'%Y%m%d_%H%M%S')"
    for (( j=0; j<bakSize; j++ )); do
        fpath=${arrOpenclashConfigBakup[$j]}
        fpathLen=${#fpath}

        # bRename
        bRename=false
        if (( 15 < fpathLen )); then
            last15chars=${fpath: -15}
            if ! is_valid_datetime "${last15chars}"; then
                bRename=true
            fi
        else
            bRename=true
        fi

        if [[ "${bRename}" == "true" ]]; then
            newFpath="${fpath}.${NowDatetime}"
            mv -f "${fpath}" "${newFpath}" &> /dev/null
            arrOpenclashConfigBakup[$j]="${newFpath}"
        fi
    done

    tar_command_string="tar c -v -f \"${tarFPath}.tar\""
    rm_command_string="rm -f"
    for (( j=0; j<bakSize-nReserve; j++ )); do
        # https://www.google.com/search?q=bash+string+equa+ignore+case&pws=0&gl=us&gws_rd=cr
        tar_command_string="${tar_command_string} \"${arrOpenclashConfigBakup[$j]}\""
        rm_command_string="${rm_command_string} \"${arrOpenclashConfigBakup[$j]}\""
    done

    if (( nReserve < bakSize )); then
        eval "$tar_command_string"
        eval "$rm_command_string"
        gzip "${tarFPath}.tar"
        assert_true "[[ -f \"${tarFPath}.tar.gz\" && ! -f \"${tarFPath}.tar\" ]]" "Compressed file \"${tarFPath}.tar\" failed."
    fi
}

tar_old_files "/tmp/tmp2/test" "/tmp/tmp2/*.yaml" 3

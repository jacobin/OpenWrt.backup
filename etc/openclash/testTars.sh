#!/bin/bash


###############################################################################
######################### function: tee_echo ##################################
###############################################################################
function tee_echo() {
    echo -e "$1" | tee -a "${DIR0}/ClashNodeSubcri.log"
}


###############################################################################
######################### function: singleton_clean_up ########################
###############################################################################
function singleton_clean_up() {
    tee_echo "\tEnd: $(date +%Y%m%d_%H%M%S)"
    exit "$1"
}


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
######################### function: tar_old_files #############################
###############################################################################
function tar_old_files() {
    # https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
    tarFPath=$(echo "$1" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    targetFPathMatchingPattern=$(echo "$2" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    nReserve=$(echo "$3" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    if [ -f "${tarFPath}.tar.gz" ]; then
        gzip -d "${tarFPath}.tar.gz"
        assert_true "[ ! -f \"${tarFPath}.tar.gz\" ]" "Failed to unzip file \"${tarFPath}.tar.gz\"."
        tar x -v -f "${tarFPath}.tar" -C "/"
        assert_true "[ -f \"${tarFPath}.tar\" ]" "tar's behavior towards file \"${tarFPath}.tar\" does not meet expectations."
        rm "${tarFPath}.tar" -f
        assert_true "[ ! -f \"${tarFPath}.tar\" ]" "Delete file \"${tarFPath}.tar\" failed."
    fi

    tar_command_string="tar c -v -f \"${tarFPath}.tar\""
    rm_command_string="rm -f"
    readarray -t arrOpenclashConfigBakup < <(ls -t -r -1 ${targetFPathMatchingPattern})
    bakSize=${#arrOpenclashConfigBakup[@]}
    for (( j=0; j<bakSize-nReserve; j++ )); do
        # https://www.google.com/search?q=bash+string+equa+ignore+case&pws=0&gl=us&gws_rd=cr
        tar_command_string="${tar_command_string} \"${arrOpenclashConfigBakup[$j]}\""
        rm_command_string="${rm_command_string} \"${arrOpenclashConfigBakup[$j]}\""
    done

    eval "$tar_command_string"
    eval "$rm_command_string"
    gzip "${tarFPath}.tar"
    assert_true "[[ -f \"${tarFPath}.tar.gz\" && ! -f \"${tarFPath}.tar\" ]]" "Compressed file \"${tarFPath}.tar\" failed."
}


tar_old_files "/etc/openclash/loop6.bak/ClashNodeSubcri.loop6" "/etc/openclash/loop6.bak/ClashNodeSubcri.loop6.2*" 5

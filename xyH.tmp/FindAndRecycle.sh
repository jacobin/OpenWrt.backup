#!/bin/bash

###############################################################################
## Place the function at the end of the script file. ##########################
###############################################################################
# https://unix.stackexchange.com/questions/724122/is-there-a-way-to-put-helper-functions-at-the-end-of-a-script-file#:~:text=Another%20way%20to%20do%20this,entire%20bash%20script%20in%20functions?
(sed '1,/^# HELPER FUNCTIONS #$/d' "$0") > $(dirname "$(readlink -f "$0")")/${baseName}.helper_function.sh
source <(sed '1,/^# HELPER FUNCTIONS #$/d' "$0")

# opkg remove "luci-i18n-adguardhome-zh-cn" "luci-app-adguardhome" "adguardhome" --force-remove --force-overwrite

declare -r searchTarget=$1
declare -ri TIMEMARK=$(date +%s)
declare -r sTIMEMARK=$(date -d @${TIMEMARK} +%Y%m%d_%H%M%S)
declare -r Recycle="/recycle"
declare -r recycleFolder="${Recycle}/${sTIMEMARK}"
declare -r fpathTemp=$(mktemp "${TMPDIR:-/tmp/}$(basename $0).${sTIMEMARK}.XXXXXXXXXXXX")

if ! validate_filename "${searchTarget}"; then
    echo "\"$1\" is NOT a valid filename"
    exit 1
fi

mkdir -p "${Recycle}"
if [ ! -d "${Recycle}" ]; then
    echo "Folder \"${Recycle}\" does not exist."
    exit 1
fi

declare -ra sysFolders=("/.config"
                        "/bin"
                        "/boot"
                        "/dev"
                        "/etc"
                        "/home"
                        "/lib"
                        "/mnt"
                        "/opt"
                        "/optcd"
                        "/proc"
                        "/root"
                        "/run"
                        "/sbin"
                        "/sys"
                        "/usr"
                        "/www")

for t in "${sysFolders[@]}"; do
    find "${t}" | grep -i "${searchTarget}" >> "${fpathTemp}"
done

readarray -t filesArr < <(cat "${fpathTemp}" | sort )
declare -i L=${#filesArr[@]}
if ((L<=0)); then
    exit 0
fi

printf "%s\n" filesArr
echo "Pressing \"YESIDO\" will delete all the files found as listed above."
echo "Pressing \"NO\" to abort the program here."
if ! YesOrNoMenu; then
    exit 0
fi

L=${#L}
let i=1
for f in "${filesArr[@]}"; do
    # https://stackoverflow.com/questions/73148822/bash-check-if-file-or-symlink-even-dangling-exists
    if [[ -h "${f}" || -e "${f}" ]]; then
        declare thisMvTargetFPath="${recycleFolder}${f}"
        declare mvTargetFolder=$(dirname "${thisMvTargetFPath}")
        mkdir -p "${mvTargetFolder}"
        mv -f "${f}" "${thisMvTargetFPath}"
        printf "%0${L}d -- %s\n" "${i}" "${f} \"${thisMvTargetFPath}\""
    fi
    ((i++))
done

exit 0
# HELPER FUNCTIONS #

###############################################################################
################################ validate_filename ############################
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
# ###############################################################################
# declare -ra arrFilenames=("/.config"
#                           "afile.txt"
#                           "b#file."
#                           "cfile.")
#
# for n in "${arrFilenames[@]}"; do
#     if validate_filename "${n}"; then
#         echo "${n}" is a valid filename.
#     else
#         echo "${n}" is NOT a valid filename.
#     fi
# done

###############################################################################
############################### YesOrNoMenu ###################################
###############################################################################
# https://askubuntu.com/questions/446156/pause-execution-and-wait-for-user-input
function YesOrNoMenu () {
    read -p "Input Selection:" YesOrNoMenuInput
    local -r NO="NO"
    local -r YESIDO="YESIDO"
    if [ "${YesOrNoMenuInput,,}" = "${YESIDO,,}" ]; then
        return 0
    elif [ "${YesOrNoMenuInput,,}" = "${NO,,}" ]; then
        return 1
    else
        YesOrNoMenu
    fi
}

###############################################################################
################################### END #######################################
###############################################################################

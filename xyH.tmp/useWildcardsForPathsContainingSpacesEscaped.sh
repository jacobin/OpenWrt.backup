#!/bin/bash

useWildcardsForPathsContainingSpaces="/tmp/tmp 2/openclash.2"
# https://stackoverflow.com/questions/6897190/problem-listing-files-in-bash-with-spaces-in-directory-path?rq=3
useWildcardsForPathsContainingSpacesEscaped=`echo "$useWildcardsForPathsContainingSpaces" | sed 's/[[:space:]]/\[[:space:]]/g'`
readarray -t arrOpenclashConfigBakup < <(ls -tc -1  ${useWildcardsForPathsContainingSpacesEscaped}*)
n=${#useWildcardsForPathsContainingSpaces}  # Number of characters to compare
bakSize=${#arrOpenclashConfigBakup[@]}
for (( j=10; j<${bakSize}; j++ )); do
    thisOldConfig=${arrOpenclashConfigBakup[$j]}
    # https://www.google.com/search?q=bash+string+compare+n+characters&pws=0&gl=us&gws_rd=cr
    substring="${thisOldConfig:0:n}"
    if [[ "${substring}" == "${useWildcardsForPathsContainingSpaces}" ]]; then
        rm "${arrOpenclashConfigBakup[$j]}"
    fi
done
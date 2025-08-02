#!/bin/bash

#******************************************************************************

clashConfigNames=()

readarray -t arrSubscri < <(cat "/etc/openclash/ClashNodeSubcri.urls")
subsSize=${#arrSubscri[@]}
if (( subsSize > 0 )); then
    for (( j=0; j<${subsSize}; j++ )); do
        subscri=${arrSubscri[$j]}
        arrSplit=(${subscri//,/ })
        fname=${arrSplit[1]}
        clashConfigNames[$j]=${fname}
        onlyName2=${clashConfigNames[$j]}
        onlyName=(${onlyName2//./ })
        echo "${onlyName}"
    done
fi

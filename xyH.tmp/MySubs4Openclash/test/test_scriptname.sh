#!/bin/bash

function aFunc() {
    ## https://stackoverflow.com/questions/192319/how-do-i-know-the-script-file-name-in-a-bash-script
    ## https://stackoverflow.com/questions/965053/extract-filename-and-extension-in-bash
    local fileNameExt=$(basename $BASH_SOURCE)
    local name="${fileNameExt%.*}"
    
    echo $name

    local name="${$(basename $BASH_SOURCE)%.*}"

    echo $name

}

aFunc
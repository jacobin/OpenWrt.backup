#!/bin/bash

# https://stackoverflow.com/questions/4073969/copy-folder-structure-without-files-from-one-location-to-another

# https://www.google.com/search?q=bash+tmp+file&pws=0&gl=us&gws_rd=cr

sourceDir=$1
targetDir=$2

dirs=$(mktemp)
targetDirs=$(mktemp)

find "${sourceDir}" -type d > ${dirs}.txt

escape_sourceDir=$(echo "${sourceDir}" | sed -e 's/[&\\/]/\\&/g')
escape_targetDir=$(echo "${targetDir}" | sed -e 's/[&\\/]/\\&/g')

sed "s/^${escape_sourceDir}/${escape_targetDir}/" ${dirs}.txt > ${targetDirs}.txt

xargs mkdir -p < ${targetDirs}.txt

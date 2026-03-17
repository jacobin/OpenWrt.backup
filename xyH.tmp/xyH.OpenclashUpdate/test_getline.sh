#!/bin/bash
# https://stackoverflow.com/questions/1521462/looping-through-the-content-of-a-file-in-bash
while IFS="" read -r p || [ -n "$p" ]
do
  printf '%s\n' "$p"
done < ./openclash_backup_file_list.txt
#!/bin/bash
input="./test3.sh"
while IFS= read -r line
do
  echo "$line"
done < "$input"
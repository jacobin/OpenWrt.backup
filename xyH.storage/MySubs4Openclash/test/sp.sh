#!/bin/bash
# Set the IFS variable to the desired delimiter
IFS=","
# Input string to be split
input="apple,banana,orange"
# Use the read command to split the input string
read -ra array <<< "$input"
# Iterate over the elements of the array
for element in "${array[@]}"
do
    echo "$element"
done
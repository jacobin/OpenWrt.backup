#!/bin/bash
# string="Doe, Jane;Smith, John;Bloggs, Joe"

# for index in {1..3}; do
#  echo "$string" | cut -d ";" -f $index
# done


# https://unix.stackexchange.com/questions/312280/split-string-by-delimiter-and-get-n-th-element
s='one_two_three_four_five'
A="$(cut -d'_' -f2 <<<"$s")"
echo "$A"

A=$(awk -F_ '{print $2}' <<< 'one_two_three_four_five')
B=$(awk -F_ '{print $4}' <<< 'one_two_three_four_five')

echo "$A"
echo "$B"

string='one_two_three_four_five'
remainder="$string"
 first="${remainder%%_*}"; remainder="${remainder#*_}"
second="${remainder%%_*}"; remainder="${remainder#*_}"
 third="${remainder%%_*}"; remainder="${remainder#*_}"
fourth="${remainder%%_*}"; remainder="${remainder#*_}"
echo $first
echo $second
echo $third
echo $fourth

# With due respect to everyone who have posted excellent answers, I wonder if we are over-engineering
# this problem. Three simple lines to just answer the question asked without generalizing:
str="one_two_three_four_five" # create a string
A=$(echo $str | awk -F_ '{print $2}') # tell awk to use _ as the delimiter and assign the second field to A
B=$(echo $str | awk -F_ '{print $4}') # tell awk to use _ as the delimiter and assign the fourth field to B

echo "$A"
echo "$B"


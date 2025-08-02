#!/bin/bash

# my_string="  This string starts with two spaces."
# another_string=" This string starts with one space."
# third_string="No leading spaces."
# fourth_string="   Three spaces."
#
# # Check for exactly two leading spaces
# if [[ "$my_string" =~ ^[[:space:]]{2}[^[:space:]] ]]; then
#   echo "\"$my_string\" starts with exactly two spaces."
# else
#   echo "\"$my_string\" does NOT start with exactly two spaces."
# fi
#
# if [[ "$another_string" =~ ^[[:space:]]{2}[^[:space:]] ]]; then
#   echo "\"$another_string\" starts with exactly two spaces."
# else
#   echo "\"$another_string\" does NOT start with exactly two spaces."
# fi
#
# if [[ "$third_string" =~ ^[[:space:]]{2}[^[:space:]] ]]; then
#   echo "\"$third_string\" starts with exactly two spaces."
# else
#   echo "\"$third_string\" does NOT start with exactly two spaces."
# fi
#
# if [[ "$fourth_string" =~ ^[[:space:]]{2}[^[:space:]] ]]; then
#   echo "\"$fourth_string\" starts with exactly two spaces."
# else
#   echo "\"$fourth_string\" does NOT start with exactly two spaces."
# fi
#
#

#!/bin/bash

begin=false
end=false

while IFS= read -r line; do
    echo "$begin|$end"
    if [[ "$begin" == true ]] && [[ "$end" == false ]]; then
        echo "tester:$line"
    fi

    if [[ "$begin" == true ]]; then
        if ! [[ "$line" == " "* ]]; then
            end=true
            echo "222222:$line"
        fi
    fi

    if [[ "$line" == "proxies:" ]]; then
        begin=true
    fi

done < "$1"

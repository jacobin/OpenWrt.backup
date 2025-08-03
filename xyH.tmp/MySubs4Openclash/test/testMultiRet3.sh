#!/bin/sh
function get_tuple()
{
    echo -e "Value1\nValue2"
}

IFS=$'\n' read -d '' -ra VALUES < <(get_tuple)
echo "${VALUES[0]}" # Value1
echo "${VALUES[1]}" # Value2



#!/bin/bash

# https://gist.github.com/mrspartak/72452c5f72b886f4422c8182190dc5ea
check_flag() {
    grep -q "$1" /proc/cpuinfo
    return $?
}

if check_flag "avx512f" && check_flag "avx512bw" && check_flag "avx512cd" && check_flag "avx512dq" && check_flag "avx512vl"; then
    echo "v4"
elif check_flag "avx" && check_flag "avx2" && check_flag "bmi1" && check_flag "bmi2" && check_flag "f16c" && check_flag "fma" && check_flag "abm" && check_flag "movbe"; then
    echo "v3"
elif check_flag "cx16" && check_flag "lahf_lm" && check_flag "popcnt" && check_flag "sse3" && check_flag "sse4_1" && check_flag "sse4_2" && check_flag "ssse3"; then
    echo "v2"
else
    echo "v1"
fi
#!/bin/bash

    TIMEBEGIN=$(date +%s%3N)
    sleep 5
    timeEnd=$(date +%s%3N)
    total_seconds=$((timeEnd-TIMEBEGIN))
    seconds=$((total_seconds % 60))
    minutes=$(((total_seconds / 60) % 60))
    hours=$((total_seconds / 3600))
    printf -v formatted_string "%02d:%02d:%02d" $hours $minutes $seconds
    printf "\tEnd: $(date +%Y%m%d_%H%M%S), time escaped:${formatted_string}"

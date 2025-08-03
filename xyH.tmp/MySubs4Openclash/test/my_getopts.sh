#!/bin/sh
## https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script
while getopts u:o: flag
do
    case "${flag}" in
        u) url=${OPTARG};;
        o) outFileName=${OPTARG};;
    esac
    eval "$1='$url'"
    eval "$2='$outFileName'"
done

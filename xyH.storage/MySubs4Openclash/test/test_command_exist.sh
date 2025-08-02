#!/bin/bash

if ! command -v teeff &> /dev/null
then
    echo "tee could not be found"
    exit 1
fi
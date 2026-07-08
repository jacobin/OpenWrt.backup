#!/bin/bash

target=$( echo "$1" | sed 's/^\.*//;s/\.*$//' \
                    | sed 's/^\/*//;s/\/*$//' )
target="./${target}"

if [ ! -f "${target}" ]; then
    echo "File \"${target}\" does not exist."
    exit 1
fi

"/etc/init.d/openclash" stop >/dev/null 2>&1
chmod +x "${target}" >/dev/null 2>&1
ln -sf "${target}" clash_meta >/dev/null 2>&1

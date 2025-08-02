#!/bin/bash

target=./mihomo-linux-amd64-compatible-v1.19.12
chmod +x "${target}"
ln -sf "${target}" clash_meta

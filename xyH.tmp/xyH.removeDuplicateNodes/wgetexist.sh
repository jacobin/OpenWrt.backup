#!/bin/bash

URL="https://raw.githubusercontent.com/barry-far/V2ray-Config/refs/heads/main/Sub1.txt"

# Use wget --spider to check for the file's existence
# -q makes wget quiet, suppressing output to stdout
# 2>&1 redirects stderr to stdout, and then /dev/null discards all output
wget --spider -q "$URL" 2>&1 > /dev/null

# Check the exit status of the wget command
if [ $? -eq 0 ]; then
  echo "The file exists at $URL."
else
  echo "The file does NOT exist at $URL or an error occurred."
fi
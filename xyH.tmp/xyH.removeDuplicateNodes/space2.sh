#!/bin/bash

my_string="  This string starts with two spaces."
another_string=" This string starts with one space."
third_string="No leading spaces."
fourth_string="   Three spaces."
fifth_string="    4 spaces."

# Check for exactly two leading spaces
if [[ "$my_string" =~ ^[[:space:]]{2}[^[:space:]] ]]; then
  echo "\"$my_string\" starts with exactly two spaces."
else
  echo "\"$my_string\" does NOT start with exactly two spaces."
fi

if [[ "$another_string" =~ ^[[:space:]]{2}[^[:space:]] ]]; then
  echo "\"$another_string\" starts with exactly two spaces."
else
  echo "\"$another_string\" does NOT start with exactly two spaces."
fi

if [[ "$third_string" =~ ^[[:space:]]{2}[^[:space:]] ]]; then
  echo "\"$third_string\" starts with exactly two spaces."
else
  echo "\"$third_string\" does NOT start with exactly two spaces."
fi

if [[ "$fourth_string" =~ ^[[:space:]]{2}[^[:space:]] ]]; then
  echo "\"$fourth_string\" starts with exactly two spaces."
else
  echo "\"$fourth_string\" does NOT start with exactly two spaces."
fi

if [[ "$fifth_string" =~ ^[[:space:]]{2}[^[:space:]] ]]; then
  echo "\"$fifth_string\" starts with exactly two spaces."
else
  echo "\"$fifth_string\" does NOT start with exactly two spaces."
fi

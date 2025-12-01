#!/bin/bash


# https://fabianlee.org/2024/06/22/yq-validate-yaml-syntax/


echo "---"                              > yaml.txt
echo " doe: \"a deer, a female deer\"" >> yaml.txt
echo " ray: \"a drop of golden sun\""  >> yaml.txt
echo " pi: 3.14159"                    >> yaml.txt
echo " xmas: true"                     >> yaml.txt
echo " french-hens: 3"                 >> yaml.txt
echo " calling-birds:"                 >> yaml.txt
echo "   - huey"                       >> yaml.txt
echo "   - dewey"                      >> yaml.txt
echo "   - louie"                      >> yaml.txt
echo "   - fred"                       >> yaml.txt
echo " xmas-fifth-day:"                >> yaml.txt
echo "   calling-birds: four"          >> yaml.txt
echo "   french-hens: 3"               >> yaml.txt
echo "   golden-rings: 5"              >> yaml.txt
echo "   partridges:"                  >> yaml.txt
echo "     count: 1"                   >> yaml.txt
echo "     location: \"a pear tree\""  >> yaml.txt
echo "   turtle-doves: two"            >> yaml.txt


echo "LS0tCiBkb2U6ICJhIGRlZXIsIGEgZmVtYWxlIGRlZXIiCiByYXk6ICJh"  > base64.txt
echo "IGRyb3Agb2YgZ29sZGVuIHN1biIKIHBpOiAzLjE0MTU5CiB4bWFzOiB0" >> base64.txt
echo "cnVlCiBmcmVuY2gtaGVuczogMwogY2FsbGluZy1iaXJkczoKICAgLSBo" >> base64.txt
echo "dWV5CiAgIC0gZGV3ZXkKICAgLSBsb3VpZQogICAtIGZyZWQKIHhtYXMt" >> base64.txt
echo "ZmlmdGgtZGF5OgogICBjYWxsaW5nLWJpcmRzOiBmb3VyCiAgIGZyZW5j" >> base64.txt
echo "aC1oZW5zOiAzCiAgIGdvbGRlbi1yaW5nczogNQogICBwYXJ0cmlkZ2Vz" >> base64.txt
echo "OgogICAgIGNvdW50OiAxCiAgICAgbG9jYXRpb246ICJhIHBlYXIgdHJl" >> base64.txt
echo "ZSIKICAgdHVydGxlLWRvdmVzOiB0d28K"                         >> base64.txt


yq --exit-status 'tag == "!!map" or tag== "!!seq"' yaml.txt &>/dev/null; echo "yq check yaml.txt, final result = $?"
yq --exit-status 'tag == "!!map" or tag== "!!seq"' base64.txt &>/dev/null; echo "yq check base64.txt, final result = $?"
base64 -d -i base64.txt &>/dev/null; echo "base64 base64.txt, final result = $?"
base64 -d -i yaml.txt &>/dev/null; echo "base64 yaml.txt, final result = $?"


rm "yaml.txt"
rm "base64.txt"

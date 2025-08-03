#!/bin/bash

sed 's/cipher: chacha20-poly1305/cipher: chacha20-ietf-poly1305/g' < "001-2ye.yaml" > "001-2ye_ed.yaml"

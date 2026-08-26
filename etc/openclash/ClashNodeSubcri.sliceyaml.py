#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
import yaml
import os
import os.path
import sys
import getopt
import re
from pathvalidate import is_valid_filename #, validate_filename
from typing import Dict, List, Any, Optional

# root@OpenWrt:~# pip list
# Package             Version
# ------------------- ----------
# aiohttp             3.9.0
# aiosignal           1.4.0
# async-timeout       4.0.3
# attrs               25.4.0
# autoflake           2.3.1
# autopep8            2.3.2
# bcrypt              3.1.7
# beautifulsoup4      4.14.3
# certifi             2025.11.12
# cffi                1.14.5
# charset-normalizer  3.4.4
# click               8.1.8
# commentjson         0.9.0
# dnspython           2.7.0
# frozenlist          1.8.0
# geoip2              5.1.0
# goto-statement      1.2
# idna                3.11
# lark-parser         0.7.8
# lxml                5.0.0
# maxminddb           2.8.2
# multidict           6.7.0
# packaging           25.0
# pathvalidate        3.3.1
# pip                 25.3
# ply                 3.11
# portalocker         3.2.0
# propcache           0.4.1
# pycodestyle         2.14.0
# pycparser           2.20
# pyflakes            3.4.0
# PyYAML              5.3.1
# requests            2.32.5
# requirements-parser 0.13.0
# setuptools          80.9.0
# six                 1.16.0
# soupsieve           2.8
# speedtest-cli       2.1.3
# texttable           1.6.3
# tomli               2.4.0
# typing_extensions   4.15.0
# tzdata              2025.3
# urllib3             2.6.2
# wheel               0.45.1
# yarl                1.22.0

###############################################################################
def load_yaml_config(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except Exception as e:
        return None

###############################################################################
def main():
    # /////////////////////////////////////////////////////////////////////
    intputYamlFPaths = []
    outputV2rayFolder = None
    outputFNamePrefix = None
    sliceSize = 0

    args = sys.argv[1:]
    options = "hi:o:f:z:"
    long_options = [ "help", "input=", "outputfolder=", "outputfnameprefix=", "slicesize=" ]

    try:
        arguments, values = getopt.getopt(args, options, long_options)
        for currentArg, currentVal in arguments:
            if currentArg in ( "-h", "--help" ):
                print( "\tpython [-h/--help] [-i/--input inputYamlPath] [-o/--outputfolder outputV2rayFolder] [-f/outputfnameprefix] [-z/--slicesize]" )
                return 0
            elif currentArg in ("-i", "--input"):
                assert os.path.isfile( currentVal )
                intputYamlFPaths.append( currentVal )
            elif currentArg in ( "-o", "--output" ):
                assert os.path.isdir( currentVal )
                outputV2rayFolder = currentVal
            elif currentArg in ( "-f", "--outputfnameprefix" ):
                assert is_valid_filename( currentVal )
                outputFNamePrefix = currentVal
            elif currentArg in ( "-z", "--slicesize" ):
                sliceSize = int(currentVal)
                assert 0 < sliceSize
    except getopt.error as err:
        print( str( err ), file=sys.stderr )

    # /////////////////////////////////////////////////////////////////////
    all_proxies = []
    for inputYamlFPath in intputYamlFPaths:
        config = load_yaml_config( inputYamlFPath )
        if config:
            proxies = config.get( 'proxies', [] )
            if proxies:
                all_proxies.extend( proxies )

    # /////////////////////////////////////////////////////////////////////
    proxyCount = len( all_proxies )
    if proxyCount == 0:
        return

    arrSliceSize = []
    arrSliceSize.append( 0 )
    # range(start, stop, step) --
    #   * start (Optional): The starting integer of the sequence. It defaults to 0.
    #   * stop (Required): The integer where the sequence ends. The loop stops before this number, meaning the stop value is exclusive.
    #   * step (Optional): The increment value between numbers. It defaults to 1
    for xCount in range( 1, proxyCount // sliceSize + 1 ):
        arrSliceSize.append( xCount * sliceSize )

    lastBox = proxyCount % sliceSize
    if 0 != lastBox:
        arrSliceSize.append( arrSliceSize[-1] + lastBox )
        xCount += 1

    assert (xCount + 1) == len(arrSliceSize)

    for xIndex in range( 0, xCount):
        proxies_obj = { "proxies": all_proxies[ arrSliceSize[ xIndex ] : arrSliceSize[ xIndex+1 ] ] }
        thisFName = outputFNamePrefix + str( xIndex+1 ).zfill(5) + '.yaml'
        thisFPath = os.path.join( outputV2rayFolder, thisFName )
        try:
            with open( thisFPath, 'w', encoding='utf-8' ) as file:
                yaml.dump( proxies_obj, file, sort_keys=False )
                file.close()
        except Exception as e:
            pass
        print( thisFName )

    assert xCount == xIndex +1

###############################################################################
if __name__ == "__main__":
    main()

################################## END ########################################

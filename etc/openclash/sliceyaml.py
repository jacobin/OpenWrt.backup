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
        print( str( err ) )

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

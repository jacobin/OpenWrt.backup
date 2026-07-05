#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
import yaml
import os
import os.path
import sys
import getopt
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
                intputYamlFPaths.append( currentVal )
            elif currentArg in ( "-o", "--output" ):
                outputV2rayFolder = currentVal
            elif currentArg in ( "-f", "--outputfnameprefix" ):
                outputFNamePrefix = currentVal
            elif currentArg in ( "-z", "--slicesize" ):
                sliceSize = int(currentVal)
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
    arrSliceSize = []
    arrSliceSize.append( 0 )
    for x in range( 1, proxyCount // sliceSize ):
        arrSliceSize.append( x * sliceSize )

    lastBox = proxyCount % sliceSize
    if 0 != lastBox:
        arrSliceSize.append( lastBox )
        x += 1

    for y in range( 0, x):
        proxies_obj = { "proxies": all_proxies[ arrSliceSize[ y ] : arrSliceSize[ y+1 ] ] }
        thisFName = outputFNamePrefix + str( y+1 ).zfill(5) + '.yaml'
        thisFPath = os.path.join( outputV2rayFolder, thisFName )
        print( thisFName )
        with open( thisFPath, "w" ) as file:
            yaml.dump( proxies_obj, file, sort_keys=False )
            file.close()

###############################################################################
if __name__ == "__main__":
    main()

################################## END ########################################

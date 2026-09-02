import csv
import operator
from operator import itemgetter
import os
import os.path
import sys
import getopt
from pathvalidate import is_valid_filename, is_valid_filepath #, validate_filename

###############################################################################
# https://www.google.com/search?q=python+csv++operator.itemgetter+NULL+index+field
def safe_itemgetter(*indices, default=None):
    # Find the maximum index we need to access
    max_idx = max(indices)

    def getter(row):
        # Pad the row with the default value if it is too short
        if len(row) <= max_idx:
            row = row + [default] * (max_idx - len(row) + 1)
        # Handle empty string fields as NULL
        return tuple(
            default if val == "" else val
            for val in itemgetter(*indices)(row)
        )

    return getter


###############################################################################
# https://www.google.com/search?q=python+sort+csv+without+header+by+fieldindex
def main():
    # /////////////////////////////////////////////////////////////////////
    inputCsvFPath = []
    outputCsvFPath = None
    byColumnIdx = 0

    args = sys.argv[1:]
    options = "hi:o:x:"
    long_options = [ "help", "input=", "output=", "byColumnIdx=" ]

    try:
        arguments, values = getopt.getopt(args, options, long_options)
        for currentArg, currentVal in arguments:
            if currentArg in ( "-h", "--help" ):
                print( "\tpython [-h/--help] [-i/--input inputCsvPath] [-o/--output outputCsvFPath] [-x/--byColumnIdx]" )
                return 0
            elif currentArg in ("-i", "--input"):
                assert is_valid_filepath( currentVal, platform="linux" )
                assert os.path.isfile( currentVal )
                inputCsvFPath = currentVal
            elif currentArg in ( "-o", "--output" ):
                assert is_valid_filepath( currentVal, platform="linux" )
                outputCsvFPath = currentVal
            elif currentArg in ( "-x", "--byColumnIdx" ):
                byColumnIdx = int(currentVal)
                assert 0 < byColumnIdx
    except getopt.error as err:
        print( str( err ), file=sys.stderr )


    with open(inputCsvFPath, 'r', newline='') as infile:
        reader = csv.reader(infile)
        # sorted_rows = sorted(reader, key=operator.itemgetter(byColumnIdx))
        sorted_rows = sorted(reader, key=safe_itemgetter(byColumnIdx, default="") )

    # https://www.google.com/search?q=python+if+filepath+is+nul+open+stdou&pws=0&gl=us&gws_rd=cr
    with open(outputCsvFPath, 'w', newline='') if outputCsvFPath else sys.stdout as outfile:
        writer = csv.writer(outfile)
        writer.writerows(sorted_rows)

###############################################################################
if __name__ == "__main__":
    main()

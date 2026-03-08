###############################################################################
import subprocess
import tempfile
from datetime import datetime
import logging
import getopt
import os
import sys

###############################################################################
def MyPrintErr(s):
    assert s
    now_time_string = str(datetime.now())
    print(now_time_string+' '+s, file=sys.stderr)
    logging.error(s)
    sys.exit(1)

###############################################################################
def MyPrintWarning(s):
    assert s
    now_time_string = str(datetime.now())
    print(now_time_string+' '+s,file=sys.stderr)
    logging.warning(s)

###############################################################################
# https://www.google.com/search?q=python+print+to+tee
class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, text):
        for f in self.files:
            f.write(text)
            f.flush() # Ensure real-time output

    def flush(self):
        for f in self.files:
            f.flush()

###############################################################################
def main():

    #/////////////////////////////getopt//////// {{
    short_options = "hu:n:r:"
    long_options = ["help", "input_url=", "output_nodes_file=", "output_url_list_file="]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        MyPrintErr(str(err))

    input_url = ""
    output_nodes_file = ""
    output_url_list_file = ""

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            current_filename = os.path.basename(__file__)
            print(f"Usage: {current_filename} -u <input_url> -n <output_nodes_file> -r <output_url_list_file>")
            sys.exit()
        elif opt in ("-u", "--input_url"):
            input_url = arg
        elif opt in ("-n", "--output_nodes_file"):
            output_nodes_file = arg
        elif opt in ("-r", "--output_url_list_file"):
            output_url_list_file = arg

    if args:
        MyPrintWarning(f"Remaining arguments: {args}")
    #/////////////////////////////getopt//////// }}

    ###############################################
    # check the inputs
    if not input_url:
        MyPrintErr("The relevant URL address must be specified.")

    if os.path.exists(output_url_list_file):
        MyPrintErr(f"The specified node list file \"{output_url_list_file}\" already exists and cannot continue. Please handle this files beforehand.")

    current_filename = os.path.basename(__file__)
    tempFPath = os.path.join(tempfile.mkdtemp(), current_filename) + '.tmp'
    tempFPath2 = os.path.join(tempfile.mkdtemp(), current_filename) + '.tmp2'

    # Call the system's wget command with the -c (continue) flag
    result = subprocess.run(["wget", "-c", input_url, "-O", tempFPath ])

    if result.returncode != 0:
        MyPrintErr("wget returned an error: {result.returncode}")

    try:
        # Open the input file for reading and the output file for writing
        with open(tempFPath, 'r') as file_in, open(tempFPath2, 'w') as file_out:
            # Iterate through each line in the input file
            for line in file_in:
                # The strip() method removes leading/trailing whitespace (including newlines)
                # Check if the line is not empty and does not start with '#'
                if line.strip() and not line.strip().startswith('#'):
                    # Write the line to the output file if it passes the filter
                    #file_out.write(line)
                    foundIdx=line.rfind("http://")
                    foundIdx2=line.rfind("https://")
                    if foundIdx >= 0 or foundIdx2 >=0:
                        beginIdx = max(foundIdx, foundIdx2)
                        line=line[beginIdx:]
                        foundSpace=line.find(" ")
                        if foundSpace > 0:
                            line=line[0:foundSpace]+'\n'
                        line = line.replace("/refs/heads", "")
                        file_out.write(line)
    except FileNotFoundError:
        MyPrintErr(f"Error: The file {tempFPath} was not found.")

    with open(tempFPath2, "r") as f:
        lines = f.readlines()
    unique_lines = set(lines)
    sorted_list = sorted(unique_lines)
    with open(output_url_list_file,'w') as f:
        f.writelines(sorted_list)

###############################################################################
if __name__ == '__main__':
    current_filename = os.path.basename(__file__)

    logging.basicConfig(filename=f'{current_filename}.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    #### Tee assist ################ {{
    # https://www.google.com/search?q=python+print+to+tee
    # Save the original standard error and open a new log file to track only errors.
    save_original_stderr = sys.stderr #  sys.__stderr__
    errlog_file = open(f'{current_filename}.track.err', 'w')
    # Redirect sys.stderr to the Tee class
    sys.stderr = Tee(save_original_stderr, errlog_file)
    ################################ }}
    # Data Stream:
    #    Python --> MyPrintErr --> { stderr --> Tee[save_stderr/original_stderr, errlog_file], logging }

    main()

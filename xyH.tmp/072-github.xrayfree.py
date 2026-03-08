###############################################################################
# https://zhuanlan.zhihu.com/p/546788844
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import getopt
import sys
import os
import re

###############################################################################
##### Evolved to using sessions instead of requests ###########################
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

    if os.path.exists(output_nodes_file):
        MyPrintErr(f"The specified node list file \"{output_nodes_file}\" already exists and cannot continue. Please handle this files beforehand.")

    #### retry_strategy ###########################
    # Configure retry strategy
    retry_strategy = Retry(
        total=3, # Total number of retries
        status_forcelist=[429, 500, 502, 503, 504], # Which status codes to retrace
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"], # Which HTTP methods are allowed to retrace
        backoff_factor=1 # Backoff factor, used to calculate the latency between each retrieval
    )

    #### adapter ##################################
    # Create an adapter configured with a connection pool to implement connection reuse and apply the retry strategy
    # By default, requests already has similar behavior, but mount provides more fine-grained control
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)

    #### custom_headers ###########################
    # The User-Agent header is commonly set to mimic a web browser
    custom_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Authorization': 'Bearer <your_token_here>'
    }

    #### session ##################################
    # Create a Session object
    session = requests.Session()
    # Assign the headers to the session object
    session.headers.update(custom_headers)
    # Mount to HTTP and HTTPS (Global Configuration)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    #### session get, similar to requests GET #####
    #url="https://github.com/githubvpn007/v2rayNvpn"
    response = session.get(input_url, timeout=5)
    if response.status_code != 200:
        MyPrintErr(f"The response.status.code of webpage \"{input_url}\" return {response.status_code}.")

    soup=BeautifulSoup(response.text, 'html.parser')
    # <p dir="auto"><a href="https://www.xrayvip.com/free.yaml" rel="nofollow">https://www.xrayvip.com/free.yaml</a></p>
    v2rayNodes=soup.find( "a", string=re.compile("https://.*\.yaml") )
    if not v2rayNodes:
        MyPrintErr("The tag(\"a\", string=re.compile(\"https://.*\.yaml\") ) NOT exists.")

    nodesInfo=v2rayNodes['href']
    if not nodesInfo:
        MyPrintErr("v2rayNodes[\'href\'] not exists.")

    f=open(output_nodes_file, 'w')
    print(nodesInfo,file=f)
    f.close()
    session.close()

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

################################## END ########################################

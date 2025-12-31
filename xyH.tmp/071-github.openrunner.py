###############################################################################
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
import sys
import time
import html
import getopt
import logging
import os.path

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
            print(f"Usage: {current_filename} -u <input_url> -f <output_nodes_file> -l <output_url_list_file>")
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

    #### check the inputs #########################
    if not input_url:
        MyPrintErr("The relevant URL address must be specified.")

    if os.path.exists(output_url_list_file):
        MyPrintErr(f"The specified link list file \"{output_url_list_file}\" already exists and cannot continue. Please handle these two files beforehand.")

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
        'Accept-Language': 'en-US,en;q=0.9', # Simulate Language
        'Authorization': 'Bearer <your_token_here>' # Sometimes a Referer header is needed to avoid being perceived as a direct request.
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
    response = session.get(input_url, timeout=5)
    if response.status_code != 200:
        MyPrintErr(f"The response.status.code of webpage \"{input_url}\" return {response.status_code}.")

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    # <p dir="auto">最新订阅地址请访问：<a href="https://free.datiya.com/" rel="nofollow"><strong>这里</strong></a></p>
    L2=soup.find_all('p')
    if not L2:
        MyPrintErr(f"The L2 <p> cannot be found on the webpage \"{input_url}\".")

    L21=L2[0]
    elesText=""
    for ele in L2:
        elesText=ele.get_text().lower()
        if "最新订阅地址请访问" in elesText:
            L21=ele;

    soup = BeautifulSoup(str(L21), 'html.parser')
    L22=soup.find('a');
    if not L22:
        MyPrintErr(f"The L22 <a> cannot be found on the tag \"{str(L21)}\".")

    L2final=L22['href']
    if not L2final:
        MyPrintErr(f"The L2final <href> cannot be found on the tag \"{str(L22)}\".")
    #print(L2final)

    response = session.get(L2final, timeout=5)
    if response.status_code != 200:
        MyPrintErr(f"The response.status.code of webpage \"{L2final}\" return {response.status_code}.")

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    # <a href=/post/20251229/ class="color-inherit dim link">【2025年12月29日】每日更新！高速免费节点，SSR/V2ray/Clash订阅链接</a>
    L3=soup.find('a', string=re.compile("【\d{4}年\d{1,2}月\d{1,2}日】每日更新！高速免费节点，.*"))
    if not L3:
        MyPrintErr("The L3 <a> cannot be found on the webpage \"{L2final}\".")
        sys.exit(9)

    L31=L3['href']
    if not L31:
        MyPrintErr(f"The L31 <href> cannot be found on the tag \"{str(L3)}\".")

    L2final=L2final.strip("/")
    L31=L31.strip("/")
    L3final=L2final+"/"+L31
    #print(L3final)

    response = session.get(L3final, timeout=5)
    if response.status_code != 200:
        MyPrintErr(f"The response.status.code of webpage \"{L3final}\" return {response.status_code}.")

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    L4=soup.find('code', string=re.compile("\d{4}\d{2}\d{2}-clash.yaml"))
    if not L4:
        MyPrintErr(f"The L4 <code> cannot be found on the webpage \"{L3final}\".")

    L4final=L4.get_text()
    #print(L4final)

    f = open(output_url_list_file, 'w')
    print(L4final ,file=f)
    f.close()

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

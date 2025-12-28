###############################################################################
from bs4 import BeautifulSoup
import os
import re
import sys
import time
import html
import getopt
import logging
import os.path

###############################################################################
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

###############################################################################
def MyPrintErr(str):
    assert str
    print(str,file=sys.stderr)
    logging.error(str)

###############################################################################
def MyPrintWarning(str):
    assert str
    print(str,file=sys.stderr)
    logging.warning(str)

###############################################################################
def cfDecodeEmail(encodedString):
    assert encodedString
    r = int(encodedString[:2], 16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

###############################################################################
def decodeNode(aNodeInfo):
    assert aNodeInfo
    cfMailBegin = aNodeInfo.find("<a class=\"")
    cfMailEnd = aNodeInfo.find("</a>")
    if -1==cfMailBegin or -1==cfMailEnd:
        return ""

    part1=aNodeInfo[0:cfMailBegin]
    part2=aNodeInfo[cfMailBegin:cfMailEnd+4]
    part3=aNodeInfo[cfMailEnd+4:]

    soup = BeautifulSoup(part2, 'html.parser')
    tagNode=soup.find('a');
    assert tagNode, "ghost"
    sCode=tagNode['data-cfemail']
    assert sCode
    decoded_email = cfDecodeEmail(sCode)
    return part1+decoded_email+part3

###############################################################################
def main():

    #/////////////////////////////getopt//////// {{
    short_options = "hu:n:r:"
    long_options = ["help", "input_url=", "output_nodes_file=", "output_url_list_file="]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        MyPrintErr(str(err))
        sys.exit(1)

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

    ###############################################
    # check the inputs
    if not input_url:
        MyPrintErr("The relevant URL address must be specified.")
        sys.exit(2)

    if os.path.exists(output_nodes_file) or os.path.exists(output_url_list_file):
        MyPrintErr(f"The specified node list file \"{output_nodes_file}\" or link list file \"{output_url_list_file}\" already exists and cannot continue. Please handle these two files beforehand.")
        sys.exit(3)

    ###############################################
    #https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request
    #https://www.google.com/search?q=python+requests.session+set+headers
    #https://www.google.com/search?q=requests.Session+mount+%E8%BF%9E%E7%BB%AD+%E5%A4%9A%E6%AC%A1
    #https://www.google.com/search?q=requests.Session+mount+%E7%9A%84

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
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    LastestClashNodeLink=soup.find('a', href=re.compile("clashnode-\d{4}\d{2}\d{2}"))
    if not LastestClashNodeLink:
        MyPrintErr("The secondary link address cannot be found on the homepage.")
        sys.exit(4)
    time.sleep(1.5) # Pauses for 1.5 seconds

    LastestClashNodeLink2=LastestClashNodeLink['href']

    # The 1st task was completed; the link address was extracted.
    response = session.get(LastestClashNodeLink2, timeout=5)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    tagYaml=soup.find(string=re.compile("\d{4}\d{2}\d{2}.yml"))
    f = open(output_url_list_file, 'w')
    print(tagYaml,file=f)
    f.close()

    # The 2nd task is extract the v2ray nodes info.
    v2rayNodesInfos=soup.find_all('pre')
    if not v2rayNodesInfos:
        MyPrintErr("List of circumvention nodes not found.")
        sys.exit(5)

    elesText=""
    for ele in v2rayNodesInfos:
        elesText=ele.get_text().lower()
        if False                    \
          or "vless"    in elesText \
          or "vmess"    in elesText \
          or "trojan"   in elesText \
          or "ssr"      in elesText \
          or "ss"       in elesText \
          or "hysteria" in elesText \
          or "quic"     in elesText \
          or "tuic"     in elesText \
          :
            elesText=str(ele)
            preBegin = elesText.find("<pre>")+5
            preEnd = elesText.find("</pre>")
            elesText=elesText[preBegin:preEnd]

    if elesText=="":
        MyPrintErr("List of circumvention nodes content not found.")
        sys.exit(6)

    lines_list = elesText.splitlines()

    f = open(output_nodes_file, 'w')
    for l in lines_list:
        original_string = html.unescape(l)
        literate=decodeNode(original_string)
        if literate:
            print(literate, file=f)
        else:
            print(original_string, file=f)
    f.close()

###############################################################################
if __name__ == '__main__':
    current_filename = os.path.basename(__file__)
    logging.basicConfig(filename=f'{current_filename}.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    main()

################################## END ########################################

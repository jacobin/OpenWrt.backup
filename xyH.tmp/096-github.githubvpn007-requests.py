###############################################################################
# https://zhuanlan.zhihu.com/p/546788844
import requests
import logging
import getopt
import sys
import os
from bs4 import BeautifulSoup

###############################################################################
current_filename = os.path.basename(__file__)
logging.basicConfig(filename=f'{current_filename}.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

###############################################################################
def MyPrintErr(str):
    print(str,file=sys.stderr)
    logging.error(str)

###############################################################################
#/////////////////////////////getopt//////////////////////////////// {{
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
        print(f"Usage: {current_filename} -u <input_url> -n <output_nodes_file> -r <output_url_list_file>")
        sys.exit()
    elif opt in ("-u", "--input_url"):
        input_url = arg
    elif opt in ("-n", "--output_nodes_file"):
        output_nodes_file = arg
    elif opt in ("-r", "--output_url_list_file"):
        output_url_list_file = arg

if args:
    MyPrintErr(f"Remaining arguments: {args}")
    sys.exit(2)
#/////////////////////////////getopt//////////////////////////////// }}

if os.path.exists(output_nodes_file):
    MyPrintErr(f"The specified node list file \"{output_nodes_file}\" already exists and cannot continue. Please handle this files beforehand.")
    sys.exit(3)

if not input_url:
    MyPrintErr(f"You must specify the URL address to download.")
    sys.exit(4)

#url="https://github.com/githubvpn007/v2rayNvpn"
response=requests.get(input_url, timeout=5)
if response.status_code == 200:
    soup=BeautifulSoup(response.text, 'html.parser')
    v2rayNodes=soup.find( "div", class_="snippet-clipboard-content notranslate position-relative overflow-auto" )
    if v2rayNodes:
        nodesInfo=v2rayNodes['data-snippet-clipboard-copy-content']
        if nodesInfo:
            f=open(output_nodes_file, 'w')
            print(nodesInfo,file=f)
            f.close()

################################## END ########################################

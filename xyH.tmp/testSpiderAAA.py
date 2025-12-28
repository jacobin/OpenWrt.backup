# https://zhuanlan.zhihu.com/p/546788844
import requests
import logging
from bs4 import BeautifulSoup

# Configure the logging to a file
logging.basicConfig(filename='096-github.githubvpn007.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#  #  # Example log messages
#  #  logging.debug("This is a debug message")
#  #  logging.info("This is an info message")
#  #  logging.warning("This is a warning message")
#  #  logging.error("This is an error message")
#  #  logging.critical("This is a critical message")

url="https://github.com/githubvpn007/v2rayNvpn"
try:
    response=requests.get(url, timeout=5)
    response.raise_for_status()
except requests.exceptions.HTTPError as errh:
    import traceback
    logging.error("Http Error:",errh)
    exit()
except requests.exceptions.ConnectionError as errc:
    import traceback
    logging.error("Error Connecting:",errc)
    exit()
except requests.exceptions.Timeout as errt:
    import traceback
    logging.error("Timeout Error:",errt)
    exit()
except requests.exceptions.RequestException as err:
    import traceback
    logging.error("OOps: Something Else",err)
    exit()
except Exception as oerr:
    import traceback
    logging.error("other Error:",oerr)
    exit()

if response.status_code == 200:
    soup=BeautifulSoup(response.text, 'html.parser')
    v2rayNodes=soup.find( "div", class_="snippet-clipboard-content notranslate position-relative overflow-auto" )
    if v2rayNodes is not None:
        print(v2rayNodes['data-snippet-clipboard-copy-content'])

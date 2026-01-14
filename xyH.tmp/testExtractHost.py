###############################################################################
# https://github.com/Epodonios/bulk-xray-v2ray-vless-vmess-...-configs/blob/main/main.py
from bs4 import BeautifulSoup, NavigableString, Tag
from datetime import datetime, timedelta, timezone
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from urllib3.util.retry import Retry
from zoneinfo import ZoneInfo
import base64
import dns.resolver # pip install dnspython
import geoip2.database
import geoip2.errors
import hashlib
import inspect
import json
import os
import os.path
import re
import requests
import shutil
import socket
import sys
import tempfile
import urllib.parse

###############################################################################
def extract_host_from_url(url):
    protocal_prefix, _, protocal_data = url.partition("://")
    if protocal_prefix == 'vmess':
        print("["+protocal_data.strip()+"]")
        json_string=None
        try:
            encoded_bytes = protocal_data.encode('utf-8')
            decoded_bytes = base64.b64decode(encoded_bytes)
            decoded_string = decoded_bytes.decode('utf-8')
            #{"add":"89.31.120.192","aid":"0","alpn":"","fp":"","host":"","id":"44537595-9ccc-4b83-8936-5f9ad3229019","net":"tcp","path":"","port":"443","ps":"@Network_442_  UAE 🇦🇪","scy":"auto","sni":"","tls":"","type":"","v":"2"}
            #{"add":"173.249.209.146","aid":"0","alpn":"","fp":"","host":"","id":"3935c2dc-dbb0-43f7-b367-fe89abe87fdf","net":"ws","path":"/","port":"20086","ps":"@Network_442_(8)","scy":"auto","sni":"","tls":"","type":"","v":"2"}
            #{"add":"hgtrojan.zabc.net","aid":"0","alpn":"","fp":"","host":"hgtrojan.zabc.net","id":"e6395c20-4571-4b34-d6b1-55a5d36e49ea","net":"ws","path":"/e6395c20","port":"2083","ps":"@Network_442_ 🇺🇸 (6)","scy":"auto","sni":"hgtrojan.zabc.net","tls":"tls","type":"","v":"2"}
            #{"add":"sy4.620720.xyz","aid":"0","alpn":"","fp":"","host":"sy4.620720.xyz","id":"516d8a7a-3f0b-41d3-bad0-246116381516","net":"ws","path":"/","port":"443","ps":"@Network_442_ 🇺🇸 (9)","scy":"auto","sni":"sy4.620720.xyz","tls":"tls","type":"","v":"2"}
            json_string = decoded_string;
        except Exception as e:
            print(f"An unexpected error occurred by Base64decode(\"{protocal_data.strip()}\"): {e}")

        if json_string:
            try:
                json_obj = json.loads(json_string)
                host=None
                if "host" in json_obj:
                    host=json_obj['host']
                if not host:
                    if "add" in json_obj:
                        host = json_obj['add']
                if host:
                    return host
            except Exception as e:
                print(f"An unexpected error occurred by Jsondecode(\"{json_string.strip()}\"): {e}")
                return None

    print(f"{protocal_prefix}, _, {protocal_data}")
    start_char = "@"
    end_char = ":"
    start_index = protocal_data.find(start_char) + len(start_char)
    end_index = protocal_data[start_index:].find(end_char)
    if end_index != -1:
        end_index += start_index
    print(f"{start_index},{end_index}")
    if start_index != -1 and end_index != -1:
        host = protocal_data[start_index:end_index]
        return host
    return None

###############################################################################
host = extract_host_from_url("socks5://Y2wQsMX39IxqBAXlxCeofJmh:5%40VOXiNET@md-chi.pvdata.host:1080#@Vpn_proxy_custom%20%E2%9C%8C%EF%B8%8F%F0%9F%A9%B8%F0%9F%96%A4%20")
print(host)
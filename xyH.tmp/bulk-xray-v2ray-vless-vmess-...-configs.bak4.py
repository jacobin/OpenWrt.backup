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
import ipaddress
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
import copy

###############################################################################
def is_valid_ip(ip_string):
    __func__ = inspect.currentframe().f_code.co_name
    """
    Checks if the given string is a valid IPv4 or IPv6 address.

    Args:
        ip_string: The string to check.

    Returns:
        True if the string is a valid IP address, False otherwise.
    """
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False
    except Exception as e:
        print(f"{__func__}(): An exception occurred: {e}")
        return False

###############################################################################
def dns_lookup_with_specific_server(domain_name, dns_server_ip):
    __func__ = inspect.currentframe().f_code.co_name
    '''
    Performs a DNS A record lookup for a domain using a specified DNS server.
    '''
    # Create a custom resolver object
    my_resolver = dns.resolver.Resolver()

    # Force the resolver to use the specified IP address
    my_resolver.nameservers = [dns_server_ip]

    try:
        # Perform the query for an A record (IPv4 address)
        answers = my_resolver.resolve(domain_name, 'A')
        #print(type(answers))
        #print(answers)
        ip_addresses = [str(answer) for answer in answers]
        return ip_addresses
    except dns.resolver.LifetimeTimeout:
        print(f"{__func__}(): Resolve '{domain_name}' error -- DNS server '{dns_server_ip}' timed out")
        return None
    except Exception as e:
        print(f"{__func__}(): Resolve '{domain_name}' error during DNS resolution: {e}")
        return None

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
def get_v2ray_links(session, url, days_ago, stringList2reserve):
    __func__ = inspect.currentframe().f_code.co_name
    try:
        response = session.get(url, timeout=5)
        if response.status_code != 200:
            print(f"{__func__}(): Failed to fetch URL (Status Code: {response.status_code})")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        #content2 = response.text.replace( "<br>", "" )
        #content3 = content2.replace( "<br/>", "" )
        #content4 = content3.replace( "</br>", "" )
        #soup = BeautifulSoup(content4, 'html.parser')

        for br in soup.find_all("br"):
            br.replace_with("\n")

        #<div class="tgme_widget_message_footer compact js-message_footer">
        #    <div class="tgme_widget_message_info short js-message_info">
        #        <span class="tgme_widget_message_meta">
        #            <a class="tgme_widget_message_date" href="https://t.me/v2rayng_fa2/1">
        #                <time datetime="2023-10-04T16:46:27+00:00" class="time">16:46</time>
        #            </a>
        #        </span>
        #    </div>
        #</div>
        #
        #<div class="tgme_widget_message_footer compact js-message_footer">
        #    <div class="tgme_widget_message_info short js-message_info">
        #        <span class="tgme_widget_message_views">1.69K</span>
        #        <span class="copyonly"> views</span>
        #        <span class="tgme_widget_message_meta">
        #            <span class="tgme_widget_message_from_author" dir="auto">🅼ₒ𝘴ᵢ</span>,&nbsp;edited &nbsp;
        #            <a class="tgme_widget_message_date" href="https://t.me/ELiV2RAY/9200">
        #                <time datetime="2025-12-26T10:01:40+00:00" class="time">10:01</time>
        #            </a>
        #        </span>
        #    </div>
        #</div>

        now = datetime.now()
        time_ago = now - timedelta(days=days_ago, hours=30, minutes=15)
        time_ago_aware = time_ago.astimezone(ZoneInfo("UTC"))

        v2ray_configs = []
        all_tags = soup.find_all()
        timeline_arrived = False
        for tag in all_tags:
            if not timeline_arrived:
                if True \
                  and tag.name == 'time' \
                  and tag.has_attr('datetime') \
                  and time_ago_aware < datetime.fromisoformat(tag['datetime'] \
                  ):
                    timeline_arrived = True
            if not timeline_arrived:
                continue
            assert timeline_arrived
            TEXT = tag.get_text(separator=" ")
            TEXTi = TEXT.lower()
            for item in stringList2reserve:
                if TEXTi.startswith(item):
                    v2ray_configs.append(TEXT)
                    break

        return v2ray_configs

    except HTTPError as e:
        print(f"{__func__}(): HTTP error occurred: {e}") # e.g., 404 Not Found, 500 Internal Server Error
    except ConnectionError as e:
        print(f"{__func__}(): Connection error occurred: {e}") # e.g., DNS failure, refused connection, no internet
    except Timeout as e:
        print(f"{__func__}(): Timeout error occurred: {e}") # Request took too long to respond
    except RequestException as e:
        # Catch any other general requests error that inherits from RequestException
        print(f"{__func__}(): An unexpected request error occurred: {e}")
    except Exception as e:
        # Catch any other potential errors (e.g., issues with Beautiful Soup parsing)
        print(f"{__func__}(): An unexpected error occurred during processing: {e}")
    else:
        # Code to run if the try block completes successfully (no exceptions)
        #print("{__func__}(): All steps completed without critical errors.")
        return None

###############################################################################
def sort_and_unique_file_lines(input_filename, output_filename):
    __func__ = inspect.currentframe().f_code.co_name
    # Use a set to automatically handle uniqueness as we read lines
    unique_lines = set()
    try:
        with open(input_filename, 'r') as f:
            for line in f:
                # Strip whitespace, including newlines, for effective comparison
                # and then add back a newline character for writing later
                stripped_line = line.strip()
                if stripped_line: # Avoid adding empty lines
                    unique_lines.add(stripped_line + '\n')
    except Exception as e:
        print(f"{__func__}(): An exception occurred when file '{input_filename}' was opened for reading.")
        return

    # Convert the set to a list and sort it
    sorted_unique_lines = sorted(list(unique_lines))

    try:
        # Write the sorted unique lines to a new file
        with open(output_filename, 'w') as f:
            f.writelines(sorted_unique_lines)
    except Exception as e:
        print(f"{__func__}(): An exception occurred when file '{output_filename}' was opened for writing.")
        return

###############################################################################
def removeoff_file_lines(input_filename, output_filename, stringList2reserve):
    __func__ = inspect.currentframe().f_code.co_name
    try:
        with open(input_filename, 'r') as f, open(output_filename, 'w') as f2:
            for line in f:
                for item in stringList2reserve:
                    if line.startswith(item):
                        f2.write(line)
    except Exception as e:
        print(f"{__func__}(): An error occurred during processing: {e}")

###############################################################################
def extract_host_from_url(url):
    __func__ = inspect.currentframe().f_code.co_name
    protocal_prefix, _, protocal_data = url.partition("://")
    if protocal_prefix == 'vmess':
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
            print(f"{__func__}(): An unexpected error occurred by Base64decode(\"{protocal_data.strip()}\"): {e}")
            json_string = None

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
                print(f"{__func__}(): An unexpected error occurred by Jsondecode(\"{json_string.strip()}\"): {e}")
                return None

    assert protocal_data
    start_char = "@"
    end_char = ":"
    start_index = protocal_data.find(start_char) + len(start_char)
    end_index = protocal_data[start_index:].find(end_char)
    if start_index == -1 or end_index == -1:
        return None
    assert start_index != -1 and end_index != -1
    end_index += start_index
    host = protocal_data[start_index:end_index]
    return host

###############################################################################
def get_region_from_ip(ip):
    __func__ = inspect.currentframe().f_code.co_name
    geo_db_path = 'GeoLite2-City.mmdb'
    try:
        with geoip2.database.Reader(geo_db_path) as reader:
            response = reader.city(ip)
            return response.country.name
    except geoip2.errors.AddressNotFoundError:
        print(f"{__func__}(): Location for IP {ip[0]} not found in the database.")
    except Exception as e:
        print(f"{__func__}(): An error occurred: {e}")
    return None

###############################################################################
def save_configs_by_region(configs):
    __func__ = inspect.currentframe().f_code.co_name
    CONFIG_FOLDER = "sub"

    if os.path.exists(CONFIG_FOLDER):
        for folder in os.listdir(CONFIG_FOLDER):
            folder_path = os.path.join(CONFIG_FOLDER, folder)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)

    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    for config in configs:
        region, _, url = config.partition(",")
        assert region
        assert url
        region_folder = os.path.join(CONFIG_FOLDER, region)
        if not os.path.exists(region_folder):
            os.makedirs(region_folder)
        try:
            with open(os.path.join(region_folder, 'config.txt'), 'a', encoding='utf-8') as file:
                file.write(url.strip() + '\n')
        except Exception as e:
            print(f"{__func__}(): An error occurred: {e}")

###############################################################################
def create_sub_section():
    __func__ = inspect.currentframe().f_code.co_name
    README_PATH = "README.md"
    CONFIG_FOLDER = "sub"

    found_sub_section = False
    content=""
    if os.path.exists(README_PATH):
        try:
            with open(README_PATH, 'r', encoding='utf-8') as readme_file:
                content = readme_file.read()
                if '## Sub' in content:
                    found_sub_section = True
        except Exception as e:
            print(f"{__func__}(): An exception occurred when file '{README_PATH}' was opened for reading.: {e}")

    new_content = ""
    new_content += "## Sub\n"
    new_content += "| Sub |\n"
    new_content += "|-----|\n"

    for root, dirs, files in os.walk(CONFIG_FOLDER):
        for directory in dirs:
            config_path = os.path.join(root, directory, 'config.txt')
            if os.path.exists(config_path):
                url = f"https://raw.githubusercontent.com/Epodonios/bulk-xray-v2ray-vless-vmess-...-configs/main/sub/{urllib.parse.quote(directory)}/config.txt"
                new_content += f"| [{directory}]({url}) |\n"
    try:
        with open(README_PATH, 'w', encoding='utf-8') as readme_file:
            if found_sub_section:
                readme_file.write(content.replace(content[content.find('## Sub'):content.find('\n\n', content.find('## Sub'))], new_content))
            else:
                readme_file.write(content + new_content)
    except Exception as e:
        print(f"{__func__}(): An exception occurred when file '{README_PATH}' was opened for writing.: {e}")

#     >>>###############################################################################
#     >>>import re
#     >>>import copy
###############################################################################
def retrive_marks(aLine, WELLKNOWN_PROTOCALs):
    PROTOCALs = copy.deepcopy(WELLKNOWN_PROTOCALs)
    # Preventing the confusion of inclusion
    pairs = [ ( "vmess://", "vmeEE://" ), ( "vless://", "vleEE://" ) ]
    for a, b in pairs:
        aLine = aLine.replace( a, b )
        PROTOCALs[ PROTOCALs.index( a ) ] = b

    all_marks=[]
    for item in PROTOCALs:
        idxs = re.finditer(item, aLine)
        if idxs:
            for idx in idxs:
                touple=(idx.start(),idx.end())
                all_marks.append(touple)

    if not all_marks:
        return None

    sorted_all_marks = sorted( all_marks, key=lambda index : index[0] )
    return sorted_all_marks

###############################################################################
def split_nodes(aLine, WELLKNOWN_PROTOCALs):
    all_marks = retrive_marks(aLine, WELLKNOWN_PROTOCALs)

    nodes=[]
    # https://www.geeksforgeeks.org/python/python-pair-iteration-in-list/
    idx_end = 0
    print(aLine)
    for x, y in zip(all_marks, all_marks[1:]):
        idx_begin = x[0]
        idx_end = y[0]
        nodes.append( aLine[idx_begin:idx_end] )
    nodes.append( aLine[idx_end:] )
    return nodes

#     >>>###############################################################################
#     >>>WELLKNOWN_PROTOCALs = [
#     >>>    'vmess://'    ,
#     >>>    'vless://'    ,
#     >>>    'ss://'       ,
#     >>>    'ssr://'      ,
#     >>>    'trojan://'   ,
#     >>>    'tuic://'     ,
#     >>>    'hysteria://' ,
#     >>>    'hy2://'      ,
#     >>>    'socks5://'   ,
#     >>>    'warp://'     ,
#     >>>    'wireguard://',
#     >>>    'snell://'    ,
#     >>>    'tuic://'     ,
#     >>>    'ssh://'      ,
#     >>>    'mieru://'    ,
#     >>>    'sudoku://'
#     >>>]
#     >>>
#     >>># split_nodes()'s example
#     >>>s="vmess://aaaaaaaaaaaaaaaaaaaaaaaaaaaAss://bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBvmess://cccccccccccccccccccccccccccccccccccccccccCvless://ddddddddddddddddddddddddddddddddddddD"
#     >>>#s="vmess://aaaaaaaaaaaaaaaaaaaaaaaaaaaA"
#     >>>#s="ss://aaaaaaaaaaaaaaaaaaaaaaaaaaaA"
#     >>>Nodes = split_nodes(s,WELLKNOWN_PROTOCALs)
#     >>>for a in Nodes:
#     >>>    print(a)
#     >>>

###############################################################################
if __name__ == "__main__":

    CURRENT_FILENAME = os.path.basename(__file__)

    # Save original stdout
    original_stdout = sys.stdout

    # Open a log file
    log_file = open(f'{CURRENT_FILENAME}.log', 'a')

    # Redirect sys.stdout to the custom Tee object
    sys.stdout = Tee(original_stdout, log_file)

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

    TELEGRAM_URLs = [
        "https://t.me/s/v2line"             ,
        "https://t.me/s/forwardv2ray"       ,
        "https://t.me/s/inikotesla"         ,
        "https://t.me/s/PrivateVPNs"        ,
        "https://t.me/s/VlessConfig"        ,
        "https://t.me/s/V2pedia"            ,
        "https://t.me/s/v2rayNG_Matsuri"    ,
        "https://t.me/s/PrivateVPNs"        ,
        "https://t.me/s/proxystore11"       ,
        "https://t.me/s/DirectVPN"          ,
        "https://t.me/s/VmessProtocol"      ,
        "https://t.me/s/OutlineVpnOfficial" ,
        "https://t.me/s/networknim"         ,
        "https://t.me/s/beiten"             ,
        "https://t.me/s/MsV2ray"            ,
        "https://t.me/s/foxrayiran"         ,
        "https://t.me/s/DailyV2RY"          ,
        "https://t.me/s/yaney_01"           ,
        "https://t.me/s/FreakConfig"        ,
        "https://t.me/s/EliV2ray"           ,
        "https://t.me/s/ServerNett"         ,
        "https://t.me/s/proxystore11"       ,
        "https://t.me/s/v2rayng_fa2"        ,
        "https://t.me/s/v2rayng_org"        ,
        "https://t.me/s/V2rayNGvpni"        ,
        "https://t.me/s/custom_14"          ,
        "https://t.me/s/v2rayNG_VPNN"       ,
        "https://t.me/s/v2ray_outlineir"    ,
        "https://t.me/s/v2_vmess"           ,
        "https://t.me/s/FreeVlessVpn"       ,
        "https://t.me/s/vmess_vless_v2rayng",
        "https://t.me/s/PrivateVPNs"        ,
        "https://t.me/s/freeland8"          ,
        "https://t.me/s/vmessiran"          ,
        "https://t.me/s/Outline_Vpn"        ,
        "https://t.me/s/vmessq"             ,
        "https://t.me/s/WeePeeN"            ,
        "https://t.me/s/V2rayNG3"           ,
        "https://t.me/s/ShadowsocksM"       ,
        "https://t.me/s/shadowsocksshop"    ,
        "https://t.me/s/v2rayan"            ,
        "https://t.me/s/ShadowSocks_s"      ,
        "https://t.me/s/VmessProtocol"      ,
        "https://t.me/s/napsternetv_config" ,
        "https://t.me/s/Easy_Free_VPN"      ,
        "https://t.me/s/V2Ray_FreedomIran"  ,
        "https://t.me/s/V2RAY_VMESS_free"   ,
        "https://t.me/s/v2ray_for_free"     ,
        "https://t.me/s/V2rayN_Free"        ,
        "https://t.me/s/free4allVPN"        ,
        "https://t.me/s/vpn_ocean"          ,
        "https://t.me/s/configV2rayForFree" ,
        "https://t.me/s/FreeV2rays"         ,
        "https://t.me/s/DigiV2ray"          ,
        "https://t.me/s/v2rayNG_VPN"        ,
        "https://t.me/s/freev2rayssr"       ,
        "https://t.me/s/v2rayn_server"      ,
        "https://t.me/s/Shadowlinkserverr"  ,
        "https://t.me/s/iranvpnet"          ,
        "https://t.me/s/vmess_iran"         ,
        "https://t.me/s/mahsaamoon1"        ,
        "https://t.me/s/V2RAY_NEW"          ,
        "https://t.me/s/v2RayChannel"       ,
        "https://t.me/s/configV2rayNG"      ,
        "https://t.me/s/config_v2ray"       ,
        "https://t.me/s/vpn_proxy_custom"   ,
        "https://t.me/s/vpnmasi"            ,
        "https://t.me/s/v2ray_custom"       ,
        "https://t.me/s/VPNCUSTOMIZE"       ,
        "https://t.me/s/HTTPCustomLand"     ,
        "https://t.me/s/vpn_proxy_custom"   ,
        "https://t.me/s/ViPVpn_v2ray"       ,
        "https://t.me/s/FreeNet1500"        ,
        "https://t.me/s/v2ray_ar"           ,
        "https://t.me/s/beta_v2ray"         ,
        "https://t.me/s/vip_vpn_2022"       ,
        "https://t.me/s/FOX_VPN66"          ,
        "https://t.me/s/VorTexIRN"          ,
        "https://t.me/s/YtTe3la"            ,
        "https://t.me/s/V2RayOxygen"        ,
        "https://t.me/s/Network_442"        ,
        "https://t.me/s/VPN_443"            ,
        "https://t.me/s/v2rayng_v"          ,
        "https://t.me/s/ultrasurf_12"       ,
        "https://t.me/s/iSeqaro"            ,
        "https://t.me/s/frev2rayng"         ,
        "https://t.me/s/frev2ray"           ,
        "https://t.me/s/FreakConfig"        ,
        "https://t.me/s/Awlix_ir"           ,
        "https://t.me/s/v2rayngvpn"         ,
        "https://t.me/s/God_CONFIG"         ,
        "https://t.me/s/Configforvpn01"     ,
    ]

    WELLKNOWN_PROTOCALs = [
        'vmess://'    ,
        'vless://'    ,
        'ss://'       ,
        'ssr://'      ,
        'trojan://'   ,
        'tuic://'     ,
        'hysteria://' ,
        'hysteria2://',
        'hy2://'      ,
        'socks5://'   ,
        'warp://'     ,
        'wireguard://',
        'snell://'    ,
        'tuic://'     ,
        'ssh://'      ,
        'mieru://'    ,
        'sudoku://'
    ]

    all_v2ray_configs = []
    for url in TELEGRAM_URLs:
        v2ray_configs = get_v2ray_links(session, url, 300, WELLKNOWN_PROTOCALs)
        if v2ray_configs:
            all_v2ray_configs.extend(v2ray_configs)

    with open("bulk-xray.txt", 'w', encoding="utf-8") as f:
        for cfg in all_v2ray_configs:
            f.write(f"[[[{cfg}]]]\n")

    exit(1)
    valid = re.compile(".*://.*")
    with open("bulk-xray.txt", 'r') as f, open("bulk-xray2.txt", 'w') as f2:
        # Iterate through each line in the file
        for line in f:
            # Optional: Use strip() to remove leading/trailing whitespace, including the newline character
            cleaned_line = line.strip()
            if valid.match(cleaned_line):
                f2.write(cleaned_line + "\n")

    with open("bulk-xray2.txt", 'r') as f, open("bulk-xray3.txt", 'w') as f2:
        for line in f:
            nodes = split_nodes( line, WELLKNOWN_PROTOCALs )
            for node in nodes:
                f2.write( node + '\n' )

    sort_and_unique_file_lines("bulk-xray3.txt", "bulk-xray4.txt")

    removeoff_file_lines("bulk-xray4.txt", "bulk-xray5.txt", WELLKNOWN_PROTOCALs )

    with open("bulk-xray5.txt", 'r') as f, open("bulk-xray6.txt", 'w') as f2:
        for url in f:
            host = extract_host_from_url(url)
            totalstring=f"{host},{url}"
            if not host:
                totalstring="WhatTheFuckingHost,{url}"
            f2.write(totalstring)

    with open("bulk-xray6.txt", 'r') as f, open("bulk-xray7.txt", 'w') as f2:
        for l in f:
            l=l.strip()
            domain, _, url = l.partition(",")
            assert domain
            assert url
            if not is_valid_ip(domain):
                ips = dns_lookup_with_specific_server(domain, '8.8.8.8')
                print(ips)
                if ips:
                    countryName = get_region_from_ip(ips[0])
                    totalstring = f"{countryName},{url}"
                    if not countryName:
                        totalstring = f"AnonymousCountry,{url}"
                    f2.write(totalstring+'\n')

    all_v2ray_configs = []
    with open("bulk-xray7.txt", 'r') as f:
        all_v2ray_configs = f.readlines()

    if all_v2ray_configs:
        save_configs_by_region(all_v2ray_configs)
        create_sub_section()
        print("Configs saved successfully.")
    else:
        print("No V2Ray configs found.")

    # To restore original behavior and close the file
    sys.stdout = original_stdout
    log_file.close()
    session.close()

################################## END ########################################

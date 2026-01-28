###############################################################################
# https://github.com/Epodonios/bulk-xray-v2ray-vless-vmess-...-configs/blob/main/main.py
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from urllib.parse import urlparse, unquote
from urllib3.util.retry import Retry
from zoneinfo import ZoneInfo
import base64
import copy
import dns.resolver # pip install dnspython
import filecmp
import geoip2.database
import geoip2.errors
import getopt
import inspect
import ipaddress
import json
import logging
import os
import os.path
import re
import requests
import shutil
import sys
import tempfile
import time
import urllib.parse

###############################################################################
def main():
    #### Preparation of environment variables #####
    __func__ = inspect.currentframe().f_code.co_name
    __script_name__ = os.path.basename(__file__)

    #### Global variables that are referenced #####
    global TELEGRAM_URLs
    global SUPPORTED_FANQIANG_PROTOCALs
    global PRESENT_DNSs
    global IPV6ADDR
    global GEO_DB_PATH

    MyPrintInfo( "Start downloading, analyzing, and extracting subscription information." )

    #{{{ Parameter preparation via getopt {{{{{{{{{
    bRedownload = False
    sDnsServer = '8.8.8.8'
    nDnsMaxSurvivalMinutes = 30
    sDnsMaxSurvivalMinutes = '30'

    opts = None
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hrd:g:t:", ["help", "redownload", "dnsserver", "geo_db_path", "dns_max_survival_minutes" ])

    except getopt.GetoptError as e:
        MyPrintErr( f'{__func__}(): An exception occurred. Details: {e}\nUsage: {__script_name__} -r<redownload> -d <dnsserver> -g <geo_db_path> -t <dns_max_survival_minutes>')

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(f'Usage: {__script_name__} -r<redownload> -d <dnsserver> -g <geo_db_path> -t <dns_max_survival_minutes>')
            sys.exit()
        elif opt in ("-r", "--redownload"):
            bRedownload = True
        elif opt in ("-d", "--dnsserver"):
            sDnsServer = arg
        elif opt in ("-g", "--geo_db_path"):
            GEO_DB_PATH = arg
        elif opt in ("-t", "--dns_max_survival_minutes"):
            sDnsMaxSurvivalMinutes = arg
        else:
            MyPrintErr( f'{__func__}(): There are non-compliant argument.\nUsage: {__script_name__} -r<redownload> -d <dnsserver> -g <geo_db_path> -t <dns_max_survival_minutes>')
    #}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}

    if not is_valid_ip( sDnsServer ):
        MyPrintErr( f"{__func__}(): The specified dnsserver parameter '{sDnsServer}' is not an IP address." )

    if not sDnsMaxSurvivalMinutes.isdigit():
        MyPrintErr( f"{__func__}(): The specified dns_max_survival_minutes parameter '{sDnsMaxSurvivalMinutes}' is not a number." )
    nDnsMaxSurvivalMinutes = int(sDnsMaxSurvivalMinutes)
    if nDnsMaxSurvivalMinutes < 0:
        MyPrintErr( f"{__func__}(): The dns_max_survival_minutes parameter '{nDnsMaxSurvivalMinutes}' cannot be less than zero." )

    if not os.path.exists( GEO_DB_PATH ):
        MyPrintErr( f"{__func__}(): The specified IP map file '{GEO_DB_PATH}' does not exist." )

    #### Preparation of environment variables 2 ###
    __script_dir__ = Path(__file__).resolve().parent
    __web_download_dir__ = f"{__script_dir__}/Epodonios/downloads"
    __Ford_assembly_line__ = f"{__script_dir__}/Epodonios/Fordline"
    F = f"{__Ford_assembly_line__}/"
    __timestamp_str__ = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #### Check system environment #################
    bFirstRun = False
    if not os.path.exists(__web_download_dir__):
        bFirstRun = True
        os.makedirs(__web_download_dir__)
    if not Path(__web_download_dir__).exists():
        MyPrintErr(f"{__func__}(): Folder '{__web_download_dir__}' dose NOT exist.")
    #----------------------------------------------
    if not os.path.exists(__Ford_assembly_line__):
        bFirstRun = True
        os.makedirs(__Ford_assembly_line__)
    if not Path(__Ford_assembly_line__).exists():
        MyPrintErr(f"{__func__}(): Folder '{__Ford_assembly_line__}' dose NOT exist.")

    #### Backup the history data ##################
    if not bFirstRun:
        temp_dir = tempfile.gettempdir()
        zip_root_dir = f"{temp_dir}/Epodonios{__timestamp_str__}"
        assert not os.path.exists( zip_root_dir )
        os.makedirs( zip_root_dir )

        src = f"{__script_dir__}/Epodonios"
        dst_parent = zip_root_dir # e.g., destination_folder
        dst = os.path.join(dst_parent, __timestamp_str__)
        shutil.copytree(src, dst) # This will create destination_folder/source_folder

        backupzip = f"{__script_dir__}/BackupEpodonios.tar.xz"
        if os.path.exists( backupzip ):
            shutil.unpack_archive( backupzip, zip_root_dir)

        sorted_dirs = sorted( list( Path( zip_root_dir ).iterdir() ) )
        for n in range( len(sorted_dirs) - 5 ):
            try:
                shutil.rmtree( sorted_dirs[n] )
            except Exception as e:
                MyPrintErr( f"{__func__}(): An exception occurred. Details: {e}" )

        shutil_compress( zip_root_dir, backupzip )

        assert os.path.exists( zip_root_dir ) and os.path.isdir( zip_root_dir )
        try:
            shutil.rmtree( zip_root_dir )
        except Exception as e:
            MyPrintErr( f"{__func__}(): Deleting directory '{zip_root_dir}' failed. Exception: {e}" )

    #### Do you want to skip the download? ########
    if bRedownload:
        download(TELEGRAM_URLs, __web_download_dir__, f"{F}a.list_downloaded_file.txt")
        filter_acceptable_files( f"{F}a.list_downloaded_file.txt", f"{F}b.accept_file.txt", f"{F}c.dead_link.txt", 7 )

    if not os.path.exists(f"{F}b.accept_file.txt"):
        MyPrintErr("Please use the -r option to download first.")

    #### extract all the v2ray links ##############
    all_v2ray_configs = []
    with open( f"{F}b.accept_file.txt", "r", encoding='utf-8' ) as f:
        for htmlfpath in f:
            v2ray_configs = extract_all_v2ray_links( htmlfpath.strip(), 365, SUPPORTED_FANQIANG_PROTOCALs )
            if v2ray_configs:
                all_v2ray_configs.extend( v2ray_configs )

    #### dump all the v2ray configs to file #######
    with open(f"{F}1.data_incomplete.txt", 'w', encoding="utf-8") as f:
        f.writelines("\n\n\n\n\n".join(all_v2ray_configs))

    #### Filter out not begining with .*:// #######
    all_double_fslash = re.compile(".*://.*")
    with \
        open(f"{F}1.data_incomplete.txt", 'r', encoding='utf-8') as f, \
        open(f"{F}2.data_incomplete.txt", 'w', encoding='utf-8') as f2:
        for line in f:
            cleaned_line = line.strip()
            if all_double_fslash.match(cleaned_line):
                f2.write(cleaned_line + "\n")

    #### Split a row containing information about multiple nodes into rows where each node occupies a separate row.
    with \
        open(f"{F}2.data_incomplete.txt", 'r', encoding='utf-8') as f, \
        open(f"{F}3.data_incomplete.txt", 'w', encoding='utf-8') as f2:
        for line in f:
            protocals = copy.deepcopy( SUPPORTED_FANQIANG_PROTOCALs )
            protocals.append( "http://" )
            protocals.append( "https://" )
            nodes = split_nodes( line, protocals )
            f2.writelines( "\n".join( nodes ) )

    sort_and_unique_file_lines( f"{F}3.data_incomplete.txt", f"{F}4.data_incomplete.txt")

    remove_unsupported_protocols( f"{F}4.data_incomplete.txt", f"{F}5.data_incomplete.txt", SUPPORTED_FANQIANG_PROTOCALs )

    with \
        open(f"{F}5.data_incomplete.txt", 'r', encoding='utf-8') as f, \
        open(f"{F}6.data_incomplete.txt", 'w', encoding='utf-8') as f2, \
        open(f"{F}d.urls_where_host_extraction_failed.txt", 'w', encoding='utf-8') as f3:
        for url in f:
            # host
            url = url.strip()
            ipv6Arr = re.findall(IPV6ADDR, url)
            if not ipv6Arr:
                host = extract_host_from_url(url)
                if not host:
                    f3.write(url + '\n')
                    host = "WhatTheFuckingHost"
            else:
                assert 1 == len(ipv6Arr)
                host = ipv6Arr[0]

            totalstring=f"{host},{url}"
            f2.write(totalstring + '\n')

    f = open_file_to_read_if_recent('present_dns.json', nDnsMaxSurvivalMinutes)
    if f:
        PRESENT_DNSs = json.load(f)
        f.close()

    with \
        open(f"{F}6.data_incomplete.txt", 'r', encoding='utf-8') as f, \
        open(f"{F}7.data_incomplete.txt", 'w', encoding='utf-8') as f2:
        for l in f:
            l=l.strip()
            domain, _, url = l.partition(",")
            assert domain
            assert url

            # ip
            ip = domain
            if not is_valid_ip(domain):
                ip = PRESENT_DNSs.get(domain, None)
                if not ip:
                    ip = 'UnableToObtain'
                    ips = dns_lookup_with_specific_server(domain, sDnsServer)
                    if ips:
                        ip = ips[0]
                        PRESENT_DNSs[domain] = ip

            # countryName
            countryName='NonExistentCountry'
            if 'UnableToObtain' != ip:
                countryName2 = get_region_from_ip( ip, GEO_DB_PATH )
                if countryName2:
                    countryName = countryName2

            f2.write(f"{countryName},{url}\n")

    all_v2ray_configs = []
    with open(f"{F}7.data_incomplete.txt", 'r', encoding='utf-8') as f:
        all_v2ray_configs = f.readlines()

    if all_v2ray_configs:
        save_configs_by_region(all_v2ray_configs)
        create_nodes_section()
        create_sub_section()
        MyPrintInfo("Configs saved successfully.")
    else:
        MyPrintInfo("No V2Ray configs found.")

    with open("present_dns.json", "w", encoding='utf-8') as f:
        json.dump(PRESENT_DNSs, f, indent=4) # 'indent=4' makes the file human-readable

###############################################################################
# format of list_downloaded_fpath: url, downloaded_tmpfile, downloaded_oldfile
def download( telegram_urls, web_download_folder, list_downloaded_fpath ):
    __func__ = inspect.currentframe().f_code.co_name

    telegram_urls = copy.deepcopy(telegram_urls)
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

    #### Download the orig webpages to htmlfile ###
    success_count = 0
    fList = open( list_downloaded_fpath, "w", encoding='utf-8')
    for url in telegram_urls:
        try:
            response = session.get(url, timeout=5)
            if response.status_code != 200:
                MyPrintWarning(f"{__func__}(): Failed to fetch URL (Status Code: {response.status_code})")
                continue
            filename=extract_filename_from_url(url)
            with open(f"{web_download_folder}/{filename}.html.tmp", "w", encoding="utf-8") as f:
                f.write(response.text)
                fList.write( f"{url},{web_download_folder}/{filename}.html.tmp,{web_download_folder}/{filename}.html\n" )
                success_count +=1
        except HTTPError as e:
            MyPrintWarning(f"{__func__}(): HTTP error occurred. Details: {e}") # e.g., 404 Not Found, 500 Internal Server Error
        except ConnectionError as e:
            MyPrintWarning(f"{__func__}(): Connection error occurred. Details: {e}") # e.g., DNS failure, refused connection, no internet
        except Timeout as e:
            MyPrintWarning(f"{__func__}(): Timeout error occurred. Details: {e}") # Request took too long to respond
        except RequestException as e:
            # Catch any other general requests error that inherits from RequestException
            MyPrintWarning(f"{__func__}(): An unexpected request error occurred. Details: {e}")
        except Exception as e:
            # Catch any other potential errors (e.g., issues with Beautiful Soup parsing)
            MyPrintWarning(f"{__func__}(): An unexpected error occurred during processing. Details: {e}")
    fList.close()
    session.close()
    return success_count

###############################################################################
def filter_acceptable_files( list_downloaded_fpath, list_accept_fpath, list_dead_links, no_changes_in_days ):
    __func__ = inspect.currentframe().f_code.co_name
    now = datetime.now()
    with \
      open( list_downloaded_fpath, "r", encoding='utf-8') as f, \
      open( list_accept_fpath, "w", encoding='utf-8' ) as f2, \
      open( list_dead_links, "w", encoding='utf-8' ) as f3:
        for l in f:
            l=l.strip()
            result = re.split(r'[,]+', l)

            url = result[0]
            tmpFPath = result[1]
            oldFPath = result[2]

            noChanges = False
            assert os.path.exists(tmpFPath)
            if os.path.exists(oldFPath):
                noChanges = filecmp.cmp(tmpFPath, oldFPath, False)
            if noChanges:
                oldFileModificationTimeStamp = os.path.getmtime(oldFPath)
                oldFileModificationDatetime = datetime.fromtimestamp(oldFileModificationTimeStamp)
                time_ago = now - timedelta(days=no_changes_in_days, hours=0, minutes=0)
                if time_ago < oldFileModificationDatetime:
                    f2.write(f"{oldFPath}\n")
                else:
                    f3.write(f"{url}\n")

            else:
                assert not noChanges
                try:
                    if os.path.exists(oldFPath):
                        os.remove(oldFPath)
                    os.rename(tmpFPath, oldFPath)
                except FileNotFoundError as e:
                    MyPrintWarning(f"{__func__}(): File not found. Details: {e}" )
                except FileExistsError as e:
                    MyPrintWarning(f"{__func__}(): New file name already exists. Details: {e}" )
                except PermissionError as e:
                    MyPrintWarning(f"{__func__}(): Permission denied. Unable to rename the file. Details: {e}" )
                except Exception as e :
                    MyPrintWarning(f"{__func__}(): An unexpected error occurred during processing: {e}" )

                f2.write(f"{oldFPath}\n")

###############################################################################
def is_valid_ip( ip_string ):
    __func__ = inspect.currentframe().f_code.co_name
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False
    except Exception as e:
        MyPrintWarning(f"{__func__}(): An exception other than a ValueError occurred. Details: {e}")
        return False

###############################################################################
# Performs a DNS A record lookup for a domain using a specified DNS server.
def dns_lookup_with_specific_server( domain_name, dns_server_ip ):
    __func__ = inspect.currentframe().f_code.co_name
    # Create a custom resolver object
    my_resolver = dns.resolver.Resolver()
    # Force the resolver to use the specified IP address
    my_resolver.nameservers = [dns_server_ip]

    try:
        # Perform the query for an A record (IPv4 address)
        answers = my_resolver.resolve(domain_name, 'A')
        #print( f"type:{type(answers)}\ndata:{answers}" )
        ip_addresses = [str(answer) for answer in answers]
        return ip_addresses
    except dns.resolver.LifetimeTimeout as e:
        MyPrintWarning(f"{__func__}(): Resolve '{domain_name}' exception -- DNS server '{dns_server_ip}' timed out. Details: {e}")
        return None
    #except dns.resolver.NXDOMAIN as e:
    #    MyPrintWarning(f"{__func__}(): Resolve '{domain_name}' exception -- The DNS query name does not exist. Details: {e}")
    #    return None
    #except dns.resolver.NoNameservers as e:
    #    MyPrintWarning(f"{__func__}(): Resolve '{domain_name}' exception -- All nameservers failed to answer the query. Details: {e}")
    #    return None
    except Exception as e:
        MyPrintWarning(f"{__func__}(): Resolve '{domain_name}' exception. Details: {e}")
        return None

###############################################################################
def MyPrintErr( s ):
    assert s
    now_time_string = str(datetime.now())
    print(now_time_string+' '+s, file=sys.stderr)
    logging.error( s )
    sys.exit(1)

###############################################################################
def MyPrintWarning( s ):
    assert s
    now_time_string = str(datetime.now())
    print(now_time_string+' '+s,file=sys.stderr)
    logging.warning( s )

###############################################################################
def MyPrintInfo( s ):
    assert s
    now_time_string = str(datetime.now())
    print(now_time_string+' '+s,file=sys.stdout)
    logging.info( s )

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
def extract_all_v2ray_links( htmlfile, days_ago, protocals ):
    with open(htmlfile, 'r', encoding='utf-8') as f: html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    '''
    Replace <br> with Newline Characters (\n) (Recommended for formatted text)
    This method modifies the parse tree in memory, replacing each <br> tag with a string newline character before extracting the text.
    This is often the most effective way to preserve the original line breaks in the output.
    '''
    for br in soup.find_all("br"):
        br.replace_with("\n")

    now = datetime.now()
    time_ago = now - timedelta(days=days_ago, hours=0, minutes=0)
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

        '''
        Avoid using `strip=true` here, as it will negate the purpose of `replace br with '\n'`.
        Also, avoid using `separator=" "` or `separator="\n"`, because these will cause expressions like `vless://...sni=<a>www.goo.en</a>` to insert a space after `sni="`, resulting in `vless://...sni= www.goo.en`.
        '''
        #TEXT = tag.get_text(separator="\n\n\n", strip=True)
        TEXT = tag.get_text()
        TEXTi = TEXT.lower()
        for item in protocals:
            if TEXTi.startswith(item):
                v2ray_configs.append(f"{TEXT}")
                break
    return v2ray_configs

###############################################################################
def sort_and_unique_file_lines( input_filename, output_filename ):
    __func__ = inspect.currentframe().f_code.co_name
    # Use a set to automatically handle uniqueness as we read lines
    unique_lines = set()
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            for line in f:
                # Strip whitespace, including newlines, for effective comparison
                # and then add back a newline character for writing later
                stripped_line = line.strip()
                if stripped_line: # Avoid adding empty lines
                    unique_lines.add(stripped_line)
    except Exception as e:
        MyPrintWarning( f"{__func__}(): An exception occurred. Details: {e}" )
        return

    # Convert the set to a list and sort it
    sorted_unique_lines = sorted(list(unique_lines))

    try:
        # Write the sorted unique lines to a new file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.writelines(line + '\n' for line in sorted_unique_lines)
    except Exception as e:
        MyPrintWarning( f"{__func__}(): An exception occurred. Details: {e}")
        return

###############################################################################
def remove_unsupported_protocols( input_filename, output_filename, protocals ):
    __func__ = inspect.currentframe().f_code.co_name
    try:
        with \
            open(input_filename, 'r', encoding='utf-8') as f, \
            open(output_filename, 'w', encoding='utf-8') as f2:
            for line in f:
                for item in protocals:
                    if line.startswith(item):
                        f2.write(line)
    except Exception as e:
        MyPrintWarning( f"{__func__}(): An error occurred. Details: {e}" )

###############################################################################
def extract_host_from_url( url ):
    __func__ = inspect.currentframe().f_code.co_name
    protocal_prefix, _, protocal_data = url.partition("://")
    if protocal_prefix == 'vmess': # Note: not all vmess links contain base64 encrypted content.
        json_string=None

        # Decoding base64 ciphertext
        try:
            encoded_bytes = protocal_data.encode('utf-8')
            decoded_bytes = base64.b64decode(encoded_bytes)
            decoded_string = decoded_bytes.decode('utf-8')
            #{"add":"89.31.120.192","aid":"0","alpn":"","fp":"","host":"","id":"44537595-9ccc-4b83-8936-5f9ad3229019","net":"tcp","path":"","port":"443","ps":"@Network_442_  UAE 🇦🇪","scy":"auto","sni":"","tls":"","type":"","v":"2"}
            #{"add":"173.249.209.146","aid":"0","alpn":"","fp":"","host":"","id":"3935c2dc-dbb0-43f7-b367-fe89abe87fdf","net":"ws","path":"/","port":"20086","ps":"@Network_442_(8)","scy":"auto","sni":"","tls":"","type":"","v":"2"}
            #{"add":"hgtrojan.zabc.net","aid":"0","alpn":"","fp":"","host":"hgtrojan.zabc.net","id":"e6395c20-4571-4b34-d6b1-55a5d36e49ea","net":"ws","path":"/e6395c20","port":"2083","ps":"@Network_442_ 🇺🇸 (6)","scy":"auto","sni":"hgtrojan.zabc.net","tls":"tls","type":"","v":"2"}
            #{"add":"sy4.620720.xyz","aid":"0","alpn":"","fp":"","host":"sy4.620720.xyz","id":"516d8a7a-3f0b-41d3-bad0-246116381516","net":"ws","path":"/","port":"443","ps":"@Network_442_ 🇺🇸 (9)","scy":"auto","sni":"sy4.620720.xyz","tls":"tls","type":"","v":"2"}
            json_string = decoded_string
        except Exception:
            json_string = None

        # If the base64 ciphertext is successfully decoded
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
                MyPrintWarning(f"{__func__}(): An unexpected error occurred by Jsondecode(\"{json_string.strip()}\"). Details: {e}")
                return None

    # Processing plaintext, including vmess plaintext
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
def get_region_from_ip( ip, geo_db_path ):
    __func__ = inspect.currentframe().f_code.co_name
    try:
        with geoip2.database.Reader(geo_db_path) as reader:
            response = reader.city(ip)
            return response.country.name
    except geoip2.errors.AddressNotFoundError as e:
        MyPrintWarning(f"{__func__}(): Location for IP {ip[0]} not found in the database. Details: {e}")
    except Exception as e:
        MyPrintWarning(f"{__func__}(): An error occurred. Details: {e}")
    return None

###############################################################################
def open_file_to_read_if_recent(file_path, max_minutes=30):
    __func__ = inspect.currentframe().f_code.co_name
    if not Path(file_path).is_file():
        return None

    modified_timestamp = os.path.getmtime(file_path)
    current_timestamp = time.time()
    time_difference_seconds = current_timestamp - modified_timestamp
    time_difference_minutes = time_difference_seconds / 60
    f = None
    if time_difference_minutes <= max_minutes:
        try:
            f = open(file_path, "r", encoding='utf-8')
        except Exception as e:
            MyPrintWarning(f"{__func__}(): An error occurred when opening '{file_path}'. Details: {e}")
            f = None

    return f

###############################################################################
def save_configs_by_region( configs ):
    __func__ = inspect.currentframe().f_code.co_name
    CONFIG_FOLDER = "sub"

    if os.path.exists(CONFIG_FOLDER):
        for folder in os.listdir(CONFIG_FOLDER):
            folder_path = os.path.join(CONFIG_FOLDER, folder)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)

    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    # https://www.google.com/search?q=python+dict+string+key+list+value
    # Create a defaultdict with a default factory of list
    map_region_urls = defaultdict( list )
    for config in configs:
        region, _, url = config.partition(",")
        assert region
        assert url
        map_region_urls[ f'{region}' ].append( url )

    try:
        for region, urls in map_region_urls.items():
            region_folder = os.path.join(CONFIG_FOLDER, region)
            assert not os.path.exists(region_folder)
            os.makedirs(region_folder)
            with open(os.path.join(region_folder, 'config.txt'), 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(url.strip() + '\n')
    except Exception as e:
        MyPrintWarning( f"{__func__}(): An error occurred. Details: {e}" )

###############################################################################
def create_sub_section():
    create_new_section(
        "README.md",
        "Sub",
        "| Sub |",
        generate_sub_table( "sub" ) )

###############################################################################
def create_nodes_section():
    create_new_section(
        "README.md",
        "Nodes",
        "| Nodes | Node Links | Node Links | Node Links | Node Links |",
        generate_nodes_table( TELEGRAM_URLs ) )

###############################################################################
def create_new_section(MDFile, section_name, table_header, new_table_content ):
    __func__ = inspect.currentframe().f_code.co_name
    found_the_section = False
    old_content=""
    if os.path.exists(MDFile):
        try:
            with open(MDFile, 'r', encoding='utf-8') as f:
                old_content = f.read()
                if f'## {section_name}' in old_content:
                    found_the_section = True
        except Exception as e:
            MyPrintWarning( f"{__func__}(): An exception occurred when file '{MDFile}' was opened for reading. Details: {e}")

    nColumn = table_header.count( '|' ) - 1

    new_content = ""
    new_content += f"## {section_name}\n{table_header}\n|"
    new_content += "---|" * nColumn
    new_content += f"\n{new_table_content.strip()}\n\n"
    try:
        with open(MDFile, 'w', encoding='utf-8') as f:
            if found_the_section:
                # r'\|\s*(\r?\n){2,}' -- Search | followed by a space or two or more newline characters (newline characters can be LF for *nx or CRLF for win).
                f.write( old_content.replace( old_content[ old_content.find( f'## {section_name}' ) : old_content.find( r'\|\s*(\r?\n){2,}', old_content.find( f'## {section_name}' ) ) ], new_content ) )
            else:
                f.write( old_content + new_content )
    except Exception as e:
        MyPrintWarning( f"{__func__}(): An exception occurred when file '{MDFile}' was opened for writing. Details: {e}" )

###############################################################################
def generate_nodes_table( telegramUrls ):
    content = ""
    # | [V2Line](https://t.me/s/v2line) | [PrivateVPNs](https://t.me/s/PrivateVPNs) | [VlessConfig](https://t.me/s/VlessConfig) | [V2pedia](https://t.me/s/V2pedia) | [v2rayNG_Matsuri](https://t.me/s/v2rayNG_Matsuri) |
    # | [inikotesla](https://t.me/s/inikotesla) | [forwardv2ray](https://t.me/s/forwardv2ray) |  |  |  |
    wrap = 0
    for url in telegramUrls:
        nodeName = extract_filename_from_url( url )
        if wrap % 5 == 0:
            content += f"\n| [{nodeName}]({url})"
        elif wrap % 5 == 4:
            content += f" | [{nodeName}]({url}) |"
        else:
            content += f" | [{nodeName}]({url})"
        wrap += 1

    nLastGroupCount = len( telegramUrls ) % 5
    if 0 != nLastGroupCount:
        for i in range( nLastGroupCount + 2 ):
            content += " | "

    return content

###############################################################################
def generate_sub_table( config_folder ):
    content = ""
    for root, dirs, files in os.walk( config_folder ):
        for directory in dirs:
            config_path = os.path.join(root, directory, 'config.txt')
            if os.path.exists( config_path ):
                url = f"https://raw.githubusercontent.com/Epodonios/bulk-xray-v2ray-vless-vmess-...-configs/main/sub/{urllib.parse.quote(directory)}/config.txt"
                content += f"| [{directory}]({url}) |\n"
    return content

###############################################################################
def _retrive_marks( aLine, fanqiang_protocals ):
    # Preventing the confusion of inclusion
    taboo_pairs = [ ( "vmess://", "vmeEE://" ), ( "vless://", "vleEE://" ) ]
    for a, b in taboo_pairs:
        aLine = aLine.replace( a, b )
        fanqiang_protocals[ fanqiang_protocals.index( a ) ] = b

    all_marks=[]
    for item in fanqiang_protocals:
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
def split_nodes( aLine, fanqiang_protocals ):
    all_marks = _retrive_marks( aLine, fanqiang_protocals )

    nodes=[]
    if all_marks:
        # https://www.geeksforgeeks.org/python/python-pair-iteration-in-list/
        idx_end = 0
        for x, y in zip(all_marks, all_marks[1:]):
            idx_begin = x[0]
            idx_end = y[0]
            nodes.append( aLine[idx_begin:idx_end] )
        nodes.append( aLine[idx_end:] )
    return nodes

###############################################################################
def extract_filename_from_url( url ):
    parsed_url = urlparse(url)
    decoded_path = unquote(parsed_url.path)
    return Path(decoded_path).name

###############################################################################
# https://www.google.com/search?q=python+compress+a+folder+best+rates
def shutil_compress( source_dir, output_filename ):
    __func__ = inspect.currentframe().f_code.co_name
    # 'xztar' uses LZMA compression, which offers the best ratio
    output_filename = output_filename.removesuffix( '.tar.xz' )
    try:
        output_path = shutil.make_archive(
            output_filename,
            'xztar', # Format: tar archive with xz compression
            root_dir = source_dir,
            base_dir = './'
        )
    except Exception as e:
        MyPrintWarning( f"{__func__}(): An error occurred. Details: {e}" )

###############################################################################
# https://github.com/Epodonios/bulk-xray-v2ray-vless-vmess-...-configs/blob/main/main.py
# https://github.com/bugbounted/telegram-configs-collector/blob/main/telegram%20channels.json
# https://github.com/mermeroo/V2rayCollector ==> https://github.com/mrvcoder/V2rayCollector/blob/main/channels.csv
# https://github.com/mermeroo/Tel-V2ray-Bot/blob/main/telegram%20channels.json
# https://github.com/Kwinshadow/TelegramV2rayCollector/blob/main/README.md
TELEGRAM_URLs = [
    "https://t.me/s/aak_vpn",
    "https://t.me/s/abadanvpn",
    "https://t.me/s/abc_cloud",
    "https://t.me/s/accountplanetir",
    "https://t.me/s/activevpn_v2ray",
    "https://t.me/s/activevshop",
    "https://t.me/s/ai_duet",
    "https://t.me/s/airdroplandcod",
    "https://t.me/s/alfred_config",
    "https://t.me/s/AliAlma_GSM",
    "https://t.me/s/alienvpn402",
    "https://t.me/s/alo_v2rayng",
    "https://t.me/s/alpha_v2ray_fazayi",
    "https://t.me/s/amirinventor2010",
    "https://t.me/s/amironetwork",
    "https://t.me/s/amirtronic",
    "https://t.me/s/ammar_taraz",
    "https://t.me/s/amozestamiratmobilei",
    "https://t.me/s/ana_service",
    "https://t.me/s/angus_vpn",
    "https://t.me/s/angus_vpn3",
    "https://t.me/s/anix_v2ray",
    "https://t.me/s/anti_ping",
    "https://t.me/s/antifilterch",
    "https://t.me/s/antifilterjadid",
    "https://t.me/s/antifilterjadid3",
    "https://t.me/s/antifilterservice",
    "https://t.me/s/antifiltervip",
    "https://t.me/s/antimeli",
    "https://t.me/s/apkgold",
    "https://t.me/s/apkprogramming",
    "https://t.me/s/apple_x1",
    "https://t.me/s/appsooner",
    "https://t.me/s/ar_cod",
    "https://t.me/s/archive_android",
    "https://t.me/s/argooo_vpn",
    "https://t.me/s/argotaz",
    "https://t.me/s/aries_init",
    "https://t.me/s/armod_iran",
    "https://t.me/s/armodchannel",
    "https://t.me/s/armodvpn",
    "https://t.me/s/arouxping",
    "https://t.me/s/arrowvpn",
    "https://t.me/s/arshia_mod_fun",
    "https://t.me/s/artemis_vpn_free",
    "https://t.me/s/artemisvpn1",
    "https://t.me/s/arv2ra",
    "https://t.me/s/arv2ray",
    "https://t.me/s/aryoovpn",
    "https://t.me/s/asak_vpn",
    "https://t.me/s/aseemanvpn",
    "https://t.me/s/asgard_vpn",
    "https://t.me/s/asintech",
    "https://t.me/s/asliveepn",
    "https://t.me/s/asr_proxy",
    "https://t.me/s/asrnovin_ir",
    "https://t.me/s/asteamvpn",
    "https://t.me/s/astrovpn_ir",
    "https://t.me/s/astrovpn_official",
    "https://t.me/s/atlanticteamchannel",
    "https://t.me/s/atovpn",
    "https://t.me/s/atvpn",
    "https://t.me/s/atvpn2",
    "https://t.me/s/avkeys",
    "https://t.me/s/Awlix_ir",
    "https://t.me/s/awv2ray",
    "https://t.me/s/axv2ray",
    "https://t.me/s/azad_intrnet",
    "https://t.me/s/azad_vpn_irm",
    "https://t.me/s/azadi_az_inja_migzare",
    "https://t.me/s/azadnetme",
    "https://t.me/s/azarbayjab1",
    "https://t.me/s/azure_v2less",
    "https://t.me/s/baipiaowansui",
    "https://t.me/s/baipiaozero",
    "https://t.me/s/baraye2121",
    "https://t.me/s/baraye3021",
    "https://t.me/s/baraye_azadi_info",
    "https://t.me/s/beiten",
    "https://t.me/s/bemolatext",
    "https://t.me/s/berice_v2",
    "https://t.me/s/best_connect_click",
    "https://t.me/s/best_ray",
    "https://t.me/s/bestvpn4030",
    "https://t.me/s/beta_v2ray",
    "https://t.me/s/betv2ray",
    "https://t.me/s/bigsmoke_config",
    "https://t.me/s/bimnetvpn",
    "https://t.me/s/bitnetvpn",
    "https://t.me/s/black8rose",
    "https://t.me/s/black_vpn1",
    "https://t.me/s/blackvpn_shop",
    "https://t.me/s/blueberrynetwork",
    "https://t.me/s/bluelearnmp",
    "https://t.me/s/blueshekan",
    "https://t.me/s/bluev2ray_2023",
    "https://t.me/s/bluev2rayng",
    "https://t.me/s/bluevpn11",
    "https://t.me/s/bluevpn111",
    "https://t.me/s/bluevpn_v2ray",
    "https://t.me/s/blunetir",
    "https://t.me/s/bolbolvpn",
    "https://t.me/s/bomb_v2rayngy",
    "https://t.me/s/boytopgvpn",
    "https://t.me/s/bpjzx2",
    "https://t.me/s/bright_vpn",
    "https://t.me/s/buffalo_vpn",
    "https://t.me/s/bug_vpn",
    "https://t.me/s/bugfreenet",
    "https://t.me/s/bypass_filter",
    "https://t.me/s/caa_chanel",
    "https://t.me/s/caa_v2ray",
    "https://t.me/s/canfigv2ray",
    "https://t.me/s/canfigvpn",
    "https://t.me/s/canfing_free",
    "https://t.me/s/canguro_english",
    "https://t.me/s/capital_net",
    "https://t.me/s/capoit",
    "https://t.me/s/castom_v2ray",
    "https://t.me/s/cattvpn",
    "https://t.me/s/catvpns",
    "https://t.me/s/cconfig_v2ray",
    "https://t.me/s/cf_clean",
    "https://t.me/s/ch_a2l",
    "https://t.me/s/ch_v2rayng",
    "https://t.me/s/chanel_config",
    "https://t.me/s/chanel_v2ray_2",
    "https://t.me/s/change_ip1",
    "https://t.me/s/charismatics_channel",
    "https://t.me/s/chatbuzzteam",
    "https://t.me/s/chv2raynp",
    "https://t.me/s/chv2raynp2",
    "https://t.me/s/circle_vpn",
    "https://t.me/s/cisco_acc",
    "https://t.me/s/clbfxs",
    "https://t.me/s/click_vpnn",
    "https://t.me/s/client_proo",
    "https://t.me/s/cloudcityy",
    "https://t.me/s/cloudflareiran",
    "https://t.me/s/club_vpn9",
    "https://t.me/s/cnfg_v2ray",
    "https://t.me/s/cnlv2rayng",
    "https://t.me/s/codvpn",
    "https://t.me/s/config_proxy_ir",
    "https://t.me/s/config_station",
    "https://t.me/s/config_v2ray",
    "https://t.me/s/config_vip7",
    "https://t.me/s/configasli",
    "https://t.me/s/configcollect",
    "https://t.me/s/configfa",
    "https://t.me/s/configfast",
    "https://t.me/s/configforvpn",
    "https://t.me/s/configforvpn01",
    "https://t.me/s/configms",
    "https://t.me/s/configpluse",
    "https://t.me/s/configpositive",
    "https://t.me/s/configpositivefree",
    "https://t.me/s/configshub",
    "https://t.me/s/configsstore",
    "https://t.me/s/configt",
    "https://t.me/s/configtell",
    "https://t.me/s/configV2rayForFree",
    "https://t.me/s/configV2rayNG",
    "https://t.me/s/configv2rayngvpn",
    "https://t.me/s/configyou",
    "https://t.me/s/confing_costume",
    "https://t.me/s/confing_v2rayy",
    "https://t.me/s/confingland",
    "https://t.me/s/confingv2raay",
    "https://t.me/s/connectback",
    "https://t.me/s/connectix",
    "https://t.me/s/connectshu",
    "https://t.me/s/cooperjon",
    "https://t.me/s/cov2ray",
    "https://t.me/s/cpuvpn",
    "https://t.me/s/cpyteel_bin",
    "https://t.me/s/cr7v2ry",
    "https://t.me/s/croownvpn",
    "https://t.me/s/crown_vpn_org",
    "https://t.me/s/cryptoguardvpn",
    "https://t.me/s/custom_14",
    "https://t.me/s/custom_config",
    "https://t.me/s/custom_v2ray",
    "https://t.me/s/customizev2ray",
    "https://t.me/s/customv2ray",
    "https://t.me/s/customvpnserver",
    "https://t.me/s/cybearvpn",
    "https://t.me/s/daily_configs",
    "https://t.me/s/dailytek",
    "https://t.me/s/dailyv2ray",
    "https://t.me/s/dailyv2ry",
    "https://t.me/s/damonconfig",
    "https://t.me/s/daorzadannet",
    "https://t.me/s/dark7web_news",
    "https://t.me/s/dark_telecom",
    "https://t.me/s/darkfiilter",
    "https://t.me/s/darkma3ter24",
    "https://t.me/s/darkproxytm",
    "https://t.me/s/darkteam_vpn",
    "https://t.me/s/darktelecom",
    "https://t.me/s/darktunnelvip1",
    "https://t.me/s/darkvpnpro",
    "https://t.me/s/daryaye_sorkhh",
    "https://t.me/s/dashv2ray",
    "https://t.me/s/dataworld_ir",
    "https://t.me/s/dayno_vpn",
    "https://t.me/s/DeamNet_proxy",
    "https://t.me/s/decentral_notification",
    "https://t.me/s/defenyx_vpn",
    "https://t.me/s/deli_servers",
    "https://t.me/s/deragv2ray",
    "https://t.me/s/dgkbza",
    "https://t.me/s/diamondproxytm",
    "https://t.me/s/digigard_vpn",
    "https://t.me/s/DigiV2ray",
    "https://t.me/s/digiv2ray23",
    "https://t.me/s/dingyue_center",
    "https://t.me/s/directvpn",
    "https://t.me/s/disconnectedconfig",
    "https://t.me/s/disvpn",
    "https://t.me/s/divare_tel",
    "https://t.me/s/dns68",
    "https://t.me/s/donald_config",
    "https://t.me/s/dr_cofing",
    "https://t.me/s/dr_v2ray",
    "https://t.me/s/dragonsource_ch",
    "https://t.me/s/dribble7",
    "https://t.me/s/drvpn_net",
    "https://t.me/s/eaglevps",
    "https://t.me/s/easy_free_vpn",
    "https://t.me/s/editby",
    "https://t.me/s/editorvpn",
    "https://t.me/s/ehsawn8",
    "https://t.me/s/eiv2ray",
    "https://t.me/s/eleutheriavpn",
    "https://t.me/s/elfv2ray",
    "https://t.me/s/elitevpnv2",
    "https://t.me/s/EliV2ray",
    "https://t.me/s/eliya_chiter0",
    "https://t.me/s/ertebatazad",
    "https://t.me/s/esetsecuritylicense",
    "https://t.me/s/Everyday_VPN",
    "https://t.me/s/evilbx",
    "https://t.me/s/exogamers",
    "https://t.me/s/exoping",
    "https://t.me/s/external_net",
    "https://t.me/s/f_nirevil",
    "https://t.me/s/falconpolv2rayng",
    "https://t.me/s/falcunargo",
    "https://t.me/s/farahvpn",
    "https://t.me/s/farda_vip",
    "https://t.me/s/farhadvapeshop",
    "https://t.me/s/faridhelp",
    "https://t.me/s/farminv2ray",
    "https://t.me/s/fasst_vpn",
    "https://t.me/s/fast_2ray",
    "https://t.me/s/fast_config_info",
    "https://t.me/s/fast_ss",
    "https://t.me/s/fastfilterr",
    "https://t.me/s/fastkanfig",
    "https://t.me/s/fati_ffx",
    "https://t.me/s/fazevpn",
    "https://t.me/s/fergalvpnmod",
    "https://t.me/s/fhkllvjkll",
    "https://t.me/s/filbar_channel",
    "https://t.me/s/filter5050",
    "https://t.me/s/filter_a",
    "https://t.me/s/filter_vpn2",
    "https://t.me/s/filterchy",
    "https://t.me/s/filtergozarnet",
    "https://t.me/s/filterintl",
    "https://t.me/s/filtershekan_channel",
    "https://t.me/s/filtershkan2",
    "https://t.me/s/filterzapata",
    "https://t.me/s/fire_vpn_channel",
    "https://t.me/s/flash_proxies",
    "https://t.me/s/flyv2ray",
    "https://t.me/s/fnet00",
    "https://t.me/s/fonix_ti",
    "https://t.me/s/forwardv2ray",
    "https://t.me/s/FOX_VPN66",
    "https://t.me/s/foxnim",
    "https://t.me/s/foxnt",
    "https://t.me/s/foxrayiran",
    "https://t.me/s/Fr33C0nfig",
    "https://t.me/s/freakconfig",
    "https://t.me/s/freakconfig1",
    "https://t.me/s/free1_vpn",
    "https://t.me/s/free1ss",
    "https://t.me/s/free4allvpn",
    "https://t.me/s/Free_HTTPCustom",
    "https://t.me/s/free_nettm",
    "https://t.me/s/free_omega",
    "https://t.me/s/free_outline_keys",
    "https://t.me/s/free_proxy_001",
    "https://t.me/s/free_v2ray_confing",
    "https://t.me/s/free_v2rayy",
    "https://t.me/s/free_v2rayyy",
    "https://t.me/s/free_v2rng",
    "https://t.me/s/free_vip3",
    "https://t.me/s/free_vpn02",
    "https://t.me/s/free_vpn_for_all_of_us",
    "https://t.me/s/free_worlld",
    "https://t.me/s/freeconfig01",
    "https://t.me/s/freeconfigv2",
    "https://t.me/s/freeconfigvpns",
    "https://t.me/s/freeconfing",
    "https://t.me/s/freedatazone1",
    "https://t.me/s/freedatazonev2ray",
    "https://t.me/s/freedom4config",
    "https://t.me/s/freedom_config",
    "https://t.me/s/Freedomnetir",
    "https://t.me/s/freeiranet",
    "https://t.me/s/freeirant",
    "https://t.me/s/freeiranweb",
    "https://t.me/s/freeland8",
    "https://t.me/s/freenapsternetv",
    "https://t.me/s/freenet",
    "https://t.me/s/FreeNet1500",
    "https://t.me/s/freenet_for_everyone",
    "https://t.me/s/freeownvpn",
    "https://t.me/s/freeshadowsock",
    "https://t.me/s/freev2flyng",
    "https://t.me/s/freev2ray2024",
    "https://t.me/s/freev2rayi",
    "https://t.me/s/freev2raym",
    "https://t.me/s/freev2rays",
    "https://t.me/s/freev2rayssh",
    "https://t.me/s/freev2rayssr",
    "https://t.me/s/freevirgoolnet",
    "https://t.me/s/freevlessvpn",
    "https://t.me/s/freevmess",
    "https://t.me/s/freevpn3327",
    "https://t.me/s/freevpnchina",
    "https://t.me/s/freevpnproxycustom",
    "https://t.me/s/freevv2rayng",
    "https://t.me/s/frev2ray",
    "https://t.me/s/frev2rayng",
    "https://t.me/s/frreevpn_ir",
    "https://t.me/s/fsv2ray",
    "https://t.me/s/funix_shope",
    "https://t.me/s/fv2ray",
    "https://t.me/s/galaxy_vpns",
    "https://t.me/s/game_file2020",
    "https://t.me/s/garnet_free",
    "https://t.me/s/ge2ray",
    "https://t.me/s/gervpn",
    "https://t.me/s/get2ray",
    "https://t.me/s/getv2ray2930",
    "https://t.me/s/gh_v2rayng",
    "https://t.me/s/ghachvpn",
    "https://t.me/s/ghalagyann",
    "https://t.me/s/ghalagyann2",
    "https://t.me/s/gigi_vpn_vip",
    "https://t.me/s/givevpn",
    "https://t.me/s/global_net_vpn",
    "https://t.me/s/god_config",
    "https://t.me/s/god_server7",
    "https://t.me/s/godv2rang",
    "https://t.me/s/goldd_v2ray",
    "https://t.me/s/goldenshiinevpn",
    "https://t.me/s/goldenvpn_v2rayy",
    "https://t.me/s/golestan_vpn",
    "https://t.me/s/golf_vpn",
    "https://t.me/s/good_v2rayy",
    "https://t.me/s/goodbyefiltering",
    "https://t.me/s/gozar7",
    "https://t.me/s/gozargahvpn",
    "https://t.me/s/gp_proxy_vpn",
    "https://t.me/s/gpair_vpn_pro2",
    "https://t.me/s/gptbottt",
    "https://t.me/s/grizzlyvpn",
    "https://t.me/s/gtexbridge",
    "https://t.me/s/guard_revil",
    "https://t.me/s/guard_vip",
    "https://t.me/s/gv2ray",
    "https://t.me/s/hack_031_2022",
    "https://t.me/s/hack_proxy",
    "https://t.me/s/hackers_link_protector",
    "https://t.me/s/hackmodvpnservers",
    "https://t.me/s/hafnetwork",
    "https://t.me/s/hajvpn",
    "https://t.me/s/hamze_tm",
    "https://t.me/s/haoshangle",
    "https://t.me/s/harvestapps",
    "https://t.me/s/hashmakvpn",
    "https://t.me/s/hassan_saboorii",
    "https://t.me/s/hatunnel_vpn",
    "https://t.me/s/hddify",
    "https://t.me/s/heinuhome",
    "https://t.me/s/helga_v2ray",
    "https://t.me/s/helix_servers",
    "https://t.me/s/hennessypro",
    "https://t.me/s/herculesl_server",
    "https://t.me/s/hermanosvpn",
    "https://t.me/s/hiddenvpnchannel",
    "https://t.me/s/hiddify",
    "https://t.me/s/hiddify_f",
    "https://t.me/s/hidifypanell",
    "https://t.me/s/hilynet",
    "https://t.me/s/hinavpn",
    "https://t.me/s/hiveping",
    "https://t.me/s/hkaa0",
    "https://t.me/s/hl_proxy",
    "https://t.me/s/ho3ino00",
    "https://t.me/s/holderproxy",
    "https://t.me/s/hologate6",
    "https://t.me/s/hologate9",
    "https://t.me/s/hooshang_vpn1",
    "https://t.me/s/hootvpm",
    "https://t.me/s/hope_net",
    "https://t.me/s/hopev2ray",
    "https://t.me/s/hopevpn",
    "https://t.me/s/hormozvpn",
    "https://t.me/s/hosseinstore_za",
    "https://t.me/s/hot_v2ry",
    "https://t.me/s/hotspotproxy",
    "https://t.me/s/hpv2ray_official",
    "https://t.me/s/httpcustomland",
    "https://t.me/s/https_config_injector",
    "https://t.me/s/huiguo62",
    "https://t.me/s/huohuaygf",
    "https://t.me/s/iamacv2ray",
    "https://t.me/s/ibv2ray",
    "https://t.me/s/icloudyshop",
    "https://t.me/s/icv2ray",
    "https://t.me/s/id_porojectt",
    "https://t.me/s/idigitalz",
    "https://t.me/s/igrsdet",
    "https://t.me/s/imrv2ray",
    "https://t.me/s/inf_service",
    "https://t.me/s/info_2it_channel",
    "https://t.me/s/inikotesla",
    "https://t.me/s/init1984",
    "https://t.me/s/injectormconf",
    "https://t.me/s/internet4iran",
    "https://t.me/s/internet_nor",
    "https://t.me/s/internetazadvmess",
    "https://t.me/s/invizibleprotm",
    "https://t.me/s/ip_cf",
    "https://t.me/s/IP_CF_Config",
    "https://t.me/s/ip_ramzi",
    "https://t.me/s/ipcloudflaretamiz",
    "https://t.me/s/iphone02016vpn",
    "https://t.me/s/ipv2ray",
    "https://t.me/s/ipv2rayng",
    "https://t.me/s/ir2nel",
    "https://t.me/s/ir_config_an",
    "https://t.me/s/ir_javann",
    "https://t.me/s/ir_nekobox",
    "https://t.me/s/ir_netproxy",
    "https://t.me/s/ir_proxyv2ray",
    "https://t.me/s/iran_access",
    "https://t.me/s/iran_mehr_vpn",
    "https://t.me/s/iran_ray",
    "https://t.me/s/iran_v2ray1",
    "https://t.me/s/iranbaxvpn",
    "https://t.me/s/iranbfilter",
    "https://t.me/s/IraneAzad_Net",
    "https://t.me/s/iranian_proxy_vpn",
    "https://t.me/s/iraniv2ray",
    "https://t.me/s/iranmedicalvpn",
    "https://t.me/s/iranmob_1",
    "https://t.me/s/iranonline_news",
    "https://t.me/s/iranproxypro",
    "https://t.me/s/iranramona",
    "https://t.me/s/iranray_vpn",
    "https://t.me/s/iransoftware90",
    "https://t.me/s/iranvipnet",
    "https://t.me/s/iranvpnet",
    "https://t.me/s/IRANVPNNET",
    "https://t.me/s/irn_vpn",
    "https://t.me/s/irv2rey",
    "https://t.me/s/isegaro",
    "https://t.me/s/iseqaro",
    "https://t.me/s/isvvpn",
    "https://t.me/s/itv2ray",
    "https://t.me/s/janusvpn",
    "https://t.me/s/javid_iran_vpn",
    "https://t.me/s/javidnamaniran",
    "https://t.me/s/jd_vpn",
    "https://t.me/s/jedal_vpn",
    "https://t.me/s/jetmtp",
    "https://t.me/s/jetupnet",
    "https://t.me/s/jeyksatan",
    "https://t.me/s/jiedianf",
    "https://t.me/s/jiedianhezu",
    "https://t.me/s/jiedianssr",
    "https://t.me/s/jiujied",
    "https://t.me/s/jokerv2ray",
    "https://t.me/s/juzibaipiao",
    "https://t.me/s/kabiritreasures",
    "https://t.me/s/kabirvpn",
    "https://t.me/s/kafing_2",
    "https://t.me/s/kakaya3in",
    "https://t.me/s/kanfig_majani",
    "https://t.me/s/kejixm123",
    "https://t.me/s/kesslervpn",
    "https://t.me/s/khalaa_vpn",
    "https://t.me/s/khoneproxy",
    "https://t.me/s/kiava",
    "https://t.me/s/kilid_stor",
    "https://t.me/s/king_network7",
    "https://t.me/s/kingmtp",
    "https://t.me/s/kingofilter",
    "https://t.me/s/kingvpnstore",
    "https://t.me/s/kinsta_service",
    "https://t.me/s/kkkkkoabvbbvbvv",
    "https://t.me/s/kopltall_vpn",
    "https://t.me/s/kurd_v2ray",
    "https://t.me/s/kurdistan_vpn_perfectt",
    "https://t.me/s/kurdvpn1",
    "https://t.me/s/kuto_proxy",
    "https://t.me/s/kuto_proxy2",
    "https://t.me/s/l_agvpn13",
    "https://t.me/s/lagvpn13",
    "https://t.me/s/lakvpn1",
    "https://t.me/s/lax_vpn",
    "https://t.me/s/lazarus2050",
    "https://t.me/s/learn_launch",
    "https://t.me/s/leastping",
    "https://t.me/s/legendery_servers",
    "https://t.me/s/leimaorg",
    "https://t.me/s/lemonshopvpn",
    "https://t.me/s/lepingshop",
    "https://t.me/s/libertas_one",
    "https://t.me/s/lightconnect_m",
    "https://t.me/s/lightning6",
    "https://t.me/s/likearzonpanell",
    "https://t.me/s/limootuursh",
    "https://t.me/s/linuxpackage",
    "https://t.me/s/lion_channel_vpn",
    "https://t.me/s/lion_channel_vpn2",
    "https://t.me/s/liq_vpn",
    "https://t.me/s/loatvpn",
    "https://t.me/s/Lockey_vpn",
    "https://t.me/s/lombo_channel",
    "https://t.me/s/lonup_m",
    "https://t.me/s/lord_ul4mo",
    "https://t.me/s/lrnbymaa",
    "https://t.me/s/lv2ray_boxl",
    "https://t.me/s/lv2rayl",
    "https://t.me/s/m_buy00",
    "https://t.me/s/mafiav2ray",
    "https://t.me/s/magickey_shop",
    "https://t.me/s/magicvpn_shop",
    "https://t.me/s/mahanfix",
    "https://t.me/s/mahanvpn",
    "https://t.me/s/mahdiserver",
    "https://t.me/s/mahdish0p",
    "https://t.me/s/mahdivpn2",
    "https://t.me/s/mahsaamoon1",
    "https://t.me/s/mahsaproxy",
    "https://t.me/s/mahxray",
    "https://t.me/s/mainmat",
    "https://t.me/s/manzariyeh_rasht",
    "https://t.me/s/maradona_vpn",
    "https://t.me/s/marzazad",
    "https://t.me/s/masirbazz",
    "https://t.me/s/mastervpnshop1",
    "https://t.me/s/maxvpnc",
    "https://t.me/s/maznet",
    "https://t.me/s/mdvpn184",
    "https://t.me/s/mdvpnsec",
    "https://t.me/s/mehradlearn",
    "https://t.me/s/mehrosaboran",
    "https://t.me/s/meli_proxyy",
    "https://t.me/s/meli_proxyyy",
    "https://t.me/s/meli_v2rayng",
    "https://t.me/s/mellii_vpn",
    "https://t.me/s/melov2ray",
    "https://t.me/s/merdesert",
    "https://t.me/s/mester_v2ray",
    "https://t.me/s/mfjdpd",
    "https://t.me/s/mftizi",
    "https://t.me/s/mgod_ping",
    "https://t.me/s/mi_pn_official",
    "https://t.me/s/migekeh",
    "https://t.me/s/migping",
    "https://t.me/s/mikasavpn",
    "https://t.me/s/mimitdl",
    "https://t.me/s/minovpnch",
    "https://t.me/s/miov2ray",
    "https://t.me/s/mitrovpn",
    "https://t.me/s/miyanbor_vpn",
    "https://t.me/s/mobilinternet",
    "https://t.me/s/mobsec",
    "https://t.me/s/mod_app31",
    "https://t.me/s/moein_insta",
    "https://t.me/s/moft_vpn",
    "https://t.me/s/moftinet",
    "https://t.me/s/moh3enivx",
    "https://t.me/s/moiinmk",
    "https://t.me/s/molovpn",
    "https://t.me/s/mood_tarinhaa",
    "https://t.me/s/moon_ping",
    "https://t.me/s/mov2ray",
    "https://t.me/s/mpmehi",
    "https://t.me/s/mpproxy",
    "https://t.me/s/mr_vpn123",
    "https://t.me/s/mrclud",
    "https://t.me/s/mrstudiosfa",
    "https://t.me/s/mruvpn",
    "https://t.me/s/mrv2raay",
    "https://t.me/s/mrv2ray",
    "https://t.me/s/mrvpn1403",
    "https://t.me/s/msv2flyng",
    "https://t.me/s/msv2ray",
    "https://t.me/s/msv2rayn",
    "https://t.me/s/msv2rayng",
    "https://t.me/s/msv2raynp",
    "https://t.me/s/mt_proxy",
    "https://t.me/s/MT_TEAM_IRAN",
    "https://t.me/s/mtconfig",
    "https://t.me/s/mtpproxy0098",
    "https://t.me/s/mtproto_dx",
    "https://t.me/s/mtproxy22_v2ray",
    "https://t.me/s/mtproxy_lists",
    "https://t.me/s/mtpv2ray",
    "https://t.me/s/my_dns_v2ray",
    "https://t.me/s/mypremium98",
    "https://t.me/s/napsternetv_config",
    "https://t.me/s/napsternetvi",
    "https://t.me/s/napsternetvirani",
    "https://t.me/s/napsterntvtm",
    "https://t.me/s/narcod_ping",
    "https://t.me/s/nepo_v2ray",
    "https://t.me/s/net_azad_1",
    "https://t.me/s/net_x1",
    "https://t.me/s/netaccount",
    "https://t.me/s/netazadchannel",
    "https://t.me/s/netbox2",
    "https://t.me/s/netcinnect",
    "https://t.me/s/netfreedom0",
    "https://t.me/s/netguardstore",
    "https://t.me/s/netmellianti",
    "https://t.me/s/netspeedservice",
    "https://t.me/s/Network_442",
    "https://t.me/s/networknim",
    "https://t.me/s/new_mtproxi",
    "https://t.me/s/new_mtproxi2",
    "https://t.me/s/next_serverpanel",
    "https://t.me/s/nicolv2ray",
    "https://t.me/s/nim_vpn_ir",
    "https://t.me/s/nitroserver_ir",
    "https://t.me/s/nitrovpne",
    "https://t.me/s/nn_vpn",
    "https://t.me/s/nob_cyber",
    "https://t.me/s/nodes_share",
    "https://t.me/s/nodpai",
    "https://t.me/s/nofilter_v2rayng",
    "https://t.me/s/nofiltering2",
    "https://t.me/s/nofilterirn",
    "https://t.me/s/noforcedheaven",
    "https://t.me/s/norbertpro_vpn",
    "https://t.me/s/novavpn1984",
    "https://t.me/s/noviin_tel",
    "https://t.me/s/novinology",
    "https://t.me/s/npv_v2ray",
    "https://t.me/s/nt_safe",
    "https://t.me/s/ntconfig",
    "https://t.me/s/ntgreenplus",
    "https://t.me/s/nufilter",
    "https://t.me/s/nufilter2",
    "https://t.me/s/nx_v2ray",
    "https://t.me/s/oceannetworks",
    "https://t.me/s/official_mtproxy",
    "https://t.me/s/ohvpn",
    "https://t.me/s/okab3_script_channel",
    "https://t.me/s/omegavp",
    "https://t.me/s/oneclickvpnkeys",
    "https://t.me/s/oonfig",
    "https://t.me/s/opensstpvpn",
    "https://t.me/s/optvpn",
    "https://t.me/s/orb_vpn",
    "https://t.me/s/orgempirenet",
    "https://t.me/s/otana_vpn",
    "https://t.me/s/outline_ir",
    "https://t.me/s/outline_kod",
    "https://t.me/s/outline_one_click",
    "https://t.me/s/outline_oneclick1",
    "https://t.me/s/Outline_Vpn",
    "https://t.me/s/outlineiran",
    "https://t.me/s/outlineopenkey",
    "https://t.me/s/outlines_vpn",
    "https://t.me/s/outlinev",
    "https://t.me/s/outlinev2rayng",
    "https://t.me/s/OutlineVpnOfficial",
    "https://t.me/s/ovpn2",
    "https://t.me/s/ownvpnofficial",
    "https://t.me/s/oxnet_ir",
    "https://t.me/s/oxygenvpn",
    "https://t.me/s/paidfill",
    "https://t.me/s/painb0y",
    "https://t.me/s/pak4you",
    "https://t.me/s/pandasng",
    "https://t.me/s/panel_free_0",
    "https://t.me/s/paoluztz",
    "https://t.me/s/pardazeshvpn",
    "https://t.me/s/parmo_vpn",
    "https://t.me/s/parsashonam",
    "https://t.me/s/parsconfigg",
    "https://t.me/s/parsv2ray1",
    "https://t.me/s/parsvip0",
    "https://t.me/s/pcv2ray",
    "https://t.me/s/perovpn",
    "https://t.me/s/persiago",
    "https://t.me/s/persian_proxy6",
    "https://t.me/s/persvpn",
    "https://t.me/s/perv2ray",
    "https://t.me/s/ph_onex",
    "https://t.me/s/phiilshekn",
    "https://t.me/s/piavpngo",
    "https://t.me/s/pin_proxy",
    "https://t.me/s/ping01pro",
    "https://t.me/s/pinkpotatocloud",
    "https://t.me/s/pistachiovpn",
    "https://t.me/s/plus_hack_er",
    "https://t.me/s/png_v2rayng",
    "https://t.me/s/polproxy",
    "https://t.me/s/ponv2ray",
    "https://t.me/s/poroxybaz",
    "https://t.me/s/pov2ray",
    "https://t.me/s/powerful1vpn",
    "https://t.me/s/powerfullvpn",
    "https://t.me/s/ppal03",
    "https://t.me/s/pqv2ray",
    "https://t.me/s/pr_guard",
    "https://t.me/s/premiumaccshoop",
    "https://t.me/s/premiumtellacc",
    "https://t.me/s/primiumv2ray",
    "https://t.me/s/priske_club",
    "https://t.me/s/priv8server",
    "https://t.me/s/privacypath",
    "https://t.me/s/private_access_guard_vpn",
    "https://t.me/s/privatevpnn",
    "https://t.me/s/PrivateVPNs",
    "https://t.me/s/pro_chaneel",
    "https://t.me/s/programmer_best",
    "https://t.me/s/prooxyk",
    "https://t.me/s/proxie",
    "https://t.me/s/proxiiraniii",
    "https://t.me/s/proxse11",
    "https://t.me/s/proxy48",
    "https://t.me/s/proxy6050",
    "https://t.me/s/proxy_confiingir",
    "https://t.me/s/proxy_emperor",
    "https://t.me/s/proxy_iranv2",
    "https://t.me/s/proxy_kafee",
    "https://t.me/s/proxy_kuto",
    "https://t.me/s/proxy_league",
    "https://t.me/s/proxy_mtm",
    "https://t.me/s/proxy_mtproto_vpns_free",
    "https://t.me/s/proxy_n1",
    "https://t.me/s/proxy_net_meli",
    "https://t.me/s/proxy_pj",
    "https://t.me/s/proxy_shadosocks",
    "https://t.me/s/proxy_v2box",
    "https://t.me/s/proxyalireayt",
    "https://t.me/s/proxydaemioutline",
    "https://t.me/s/proxyfacts",
    "https://t.me/s/proxyfn",
    "https://t.me/s/proxyfull",
    "https://t.me/s/proxyhubc",
    "https://t.me/s/proxyirancel",
    "https://t.me/s/proxylegram",
    "https://t.me/s/proxymaann",
    "https://t.me/s/proxymy2",
    "https://t.me/s/ProxyPJ",
    "https://t.me/s/proxyporsoat",
    "https://t.me/s/proxyrunner",
    "https://t.me/s/proxysee",
    "https://t.me/s/proxysharecn",
    "https://t.me/s/proxyskyy",
    "https://t.me/s/proxystore11",
    "https://t.me/s/proxystore666",
    "https://t.me/s/proxysudo",
    "https://t.me/s/proxytelegramandwahtsappofficial",
    "https://t.me/s/proxyvpnvip",
    "https://t.me/s/proxyy",
    "https://t.me/s/proxyymeliii",
    "https://t.me/s/prrofile_purple",
    "https://t.me/s/prroxyng",
    "https://t.me/s/psiphonf",
    "https://t.me/s/pubg_vpn_ir",
    "https://t.me/s/public504",
    "https://t.me/s/puni_shop_v2rayng",
    "https://t.me/s/pusyvpn",
    "https://t.me/s/pydriclub",
    "https://t.me/s/qafor_1",
    "https://t.me/s/qeshmserver",
    "https://t.me/s/qiuyue2",
    "https://t.me/s/qrv2ray",
    "https://t.me/s/qv2raychannel",
    "https://t.me/s/qvpnn",
    "https://t.me/s/qwjhfx",
    "https://t.me/s/rabbit2vpn",
    "https://t.me/s/rasadvpn",
    "https://t.me/s/ravenxer",
    "https://t.me/s/rayanconf",
    "https://t.me/s/rayvps",
    "https://t.me/s/reality_daily",
    "https://t.me/s/realvpnmaster",
    "https://t.me/s/red2ray",
    "https://t.me/s/relaxv2ray",
    "https://t.me/s/renetvip",
    "https://t.me/s/renetvpn",
    "https://t.me/s/repairms",
    "https://t.me/s/rexusvpn",
    "https://t.me/s/rez1vpn",
    "https://t.me/s/rezadehqan_ir",
    "https://t.me/s/rezaw_server",
    "https://t.me/s/rima_vpn",
    "https://t.me/s/rivorvpn",
    "https://t.me/s/rk_filtershking",
    "https://t.me/s/rnrifci",
    "https://t.me/s/rohv2ray",
    "https://t.me/s/romax_vpn",
    "https://t.me/s/roshdcollection",
    "https://t.me/s/royal_shop87",
    "https://t.me/s/royalping_ir",
    "https://t.me/s/rskhivpn",
    "https://t.me/s/rsv2ray",
    "https://t.me/s/rxv2ray",
    "https://t.me/s/sabz_v2ray",
    "https://t.me/s/SafeNet_Server",
    "https://t.me/s/SafeNetIR",
    "https://t.me/s/saferoadnet",
    "https://t.me/s/safous_vpn",
    "https://t.me/s/sajad_titan_s_t_n_v2ray",
    "https://t.me/s/samiv2ray",
    "https://t.me/s/satafkompani",
    "https://t.me/s/satarvpn1",
    "https://t.me/s/satellitenewspersian",
    "https://t.me/s/savagenet",
    "https://t.me/s/savagev2ray",
    "https://t.me/s/saveproxy",
    "https://t.me/s/sayco_proxy",
    "https://t.me/s/securenetwork1",
    "https://t.me/s/securit_y_breach",
    "https://t.me/s/selinc",
    "https://t.me/s/server01012",
    "https://t.me/s/server444",
    "https://t.me/s/server_housing03",
    "https://t.me/s/server_nekobox",
    "https://t.me/s/server_vip_ir",
    "https://t.me/s/serverii",
    "https://t.me/s/servernett",
    "https://t.me/s/serversiran11",
    "https://t.me/s/serverv2ray00",
    "https://t.me/s/set_v2ray",
    "https://t.me/s/seven_ping",
    "https://t.me/s/sevenvpnchannel",
    "https://t.me/s/sezar_sec",
    "https://t.me/s/shadow_socks1",
    "https://t.me/s/shadow_v2ray",
    "https://t.me/s/Shadowlinkserverr",
    "https://t.me/s/shadowproxy66",
    "https://t.me/s/shadowrocketv2ray",
    "https://t.me/s/ShadowSocks_s",
    "https://t.me/s/shadowsockskeys",
    "https://t.me/s/ShadowsocksM",
    "https://t.me/s/shadowsocksserv",
    "https://t.me/s/shadowsocksservers",
    "https://t.me/s/shadowsocksshop",
    "https://t.me/s/share_nodes",
    "https://t.me/s/sharecentrepro",
    "https://t.me/s/shconfig",
    "https://t.me/s/shh_proxy",
    "https://t.me/s/shokhmiplus",
    "https://t.me/s/shopingv2ray",
    "https://t.me/s/shopzonix",
    "https://t.me/s/sifev2ray",
    "https://t.me/s/sifrdvpn",
    "https://t.me/s/sigma_tic",
    "https://t.me/s/silvaserver",
    "https://t.me/s/sinamobail",
    "https://t.me/s/sitefilter",
    "https://t.me/s/skipvip",
    "https://t.me/s/skivpn",
    "https://t.me/s/sobi_vpn",
    "https://t.me/s/sobyv2ray",
    "https://t.me/s/sockcs_http",
    "https://t.me/s/socks5r",
    "https://t.me/s/socks5tobefree",
    "https://t.me/s/sockshttp_vpn",
    "https://t.me/s/soranvpn",
    "https://t.me/s/soskeynet",
    "https://t.me/s/sourcefreefilter",
    "https://t.me/s/sourcevipn",
    "https://t.me/s/spcware",
    "https://t.me/s/spdnet",
    "https://t.me/s/speedconfig00",
    "https://t.me/s/spikevpn",
    "https://t.me/s/springhq",
    "https://t.me/s/springv2ray",
    "https://t.me/s/srcvpn",
    "https://t.me/s/srv2ray",
    "https://t.me/s/ssrtool",
    "https://t.me/s/standvpn",
    "https://t.me/s/star_hack_100",
    "https://t.me/s/starconfigs1",
    "https://t.me/s/starv2rayn",
    "https://t.me/s/staticvpn",
    "https://t.me/s/strongprotocol",
    "https://t.me/s/subscription8",
    "https://t.me/s/sudovpn",
    "https://t.me/s/summertimeus",
    "https://t.me/s/SvnTeam",
    "https://t.me/s/talentvpn",
    "https://t.me/s/tawanaclub",
    "https://t.me/s/tc_v2ray",
    "https://t.me/s/teamkingo",
    "https://t.me/s/teamvpnpro",
    "https://t.me/s/techno_v2rayvpn",
    "https://t.me/s/tehranargo",
    "https://t.me/s/tehranargo1",
    "https://t.me/s/tehranfreevpn",
    "https://t.me/s/tehron98",
    "https://t.me/s/teleking_vip",
    "https://t.me/s/telmavpn",
    "https://t.me/s/tenzovpn",
    "https://t.me/s/tg233boy",
    "https://t.me/s/tgvpn6",
    "https://t.me/s/thehotvpn",
    "https://t.me/s/thunderv2ray",
    "https://t.me/s/tiger_hack_king",
    "https://t.me/s/tiktok_proxy",
    "https://t.me/s/tiny_vpn_official",
    "https://t.me/s/titan_v2rayng",
    "https://t.me/s/titan_v2rayvpn",
    "https://t.me/s/tiv2ray",
    "https://t.me/s/tkm_server",
    "https://t.me/s/tls_v2ray",
    "https://t.me/s/tm_bax_v2ray",
    "https://t.me/s/tm_vpn_king_bott",
    "https://t.me/s/tm_vpn_ogrysy",
    "https://t.me/s/tmnet_news",
    "https://t.me/s/tmno1vpn",
    "https://t.me/s/tmv2ray",
    "https://t.me/s/tokyonetwork",
    "https://t.me/s/tongtiange",
    "https://t.me/s/top2rayy",
    "https://t.me/s/top_neti",
    "https://t.me/s/topvpn02",
    "https://t.me/s/torang_vpn",
    "https://t.me/s/toucan_vpn",
    "https://t.me/s/tov2rayy",
    "https://t.me/s/toyota_proxy",
    "https://t.me/s/toyota_proxyyyy",
    "https://t.me/s/trand_farsi",
    "https://t.me/s/tunder_vpn",
    "https://t.me/s/TunelProV2",
    "https://t.me/s/tunelvip",
    "https://t.me/s/tunssh",
    "https://t.me/s/turboo_server",
    "https://t.me/s/turbov2r",
    "https://t.me/s/tv2rayrr",
    "https://t.me/s/tv_v2ray",
    "https://t.me/s/uciranir",
    "https://t.me/s/ultrasurf_12",
    "https://t.me/s/uniquenett",
    "https://t.me/s/univstar",
    "https://t.me/s/unlimiteddev",
    "https://t.me/s/uraniumvpn",
    "https://t.me/s/uvpn_org",
    "https://t.me/s/uvpnir",
    "https://t.me/s/v222ray",
    "https://t.me/s/v22rayngg",
    "https://t.me/s/v2_kurd",
    "https://t.me/s/v2_r_ayng",
    "https://t.me/s/v2_team",
    "https://t.me/s/v2_vmess",
    "https://t.me/s/v2advicr",
    "https://t.me/s/v2ang",
    "https://t.me/s/v2aryng_vpn",
    "https://t.me/s/v2bamdad",
    "https://t.me/s/v2boxng74",
    "https://t.me/s/v2city",
    "https://t.me/s/v2conf",
    "https://t.me/s/v2dotcom",
    "https://t.me/s/v2fast100",
    "https://t.me/s/v2fetch",
    "https://t.me/s/v2fox_config",
    "https://t.me/s/v2fre",
    "https://t.me/s/v2freenet",
    "https://t.me/s/v2freevpn",
    "https://t.me/s/v2gng",
    "https://t.me/s/v2graphy",
    "https://t.me/s/v2hamid",
    "https://t.me/s/v2icy",
    "https://t.me/s/v2line",
    "https://t.me/s/v2logy",
    "https://t.me/s/v2meowcf",
    "https://t.me/s/v2mod",
    "https://t.me/s/v2mystery",
    "https://t.me/s/v2net_iran",
    "https://t.me/s/v2ngfast",
    "https://t.me/s/v2pedia",
    "https://t.me/s/v2proxy",
    "https://t.me/s/v2ra2",
    "https://t.me/s/v2ra_ng_iran",
    "https://t.me/s/v2raand",
    "https://t.me/s/v2raayngconfig",
    "https://t.me/s/v2rang_255",
    "https://t.me/s/v2rang_da",
    "https://t.me/s/v2range",
    "https://t.me/s/v2rangkanal",
    "https://t.me/s/v2raxx",
    "https://t.me/s/v2ray16",
    "https://t.me/s/v2ray1_ng",
    "https://t.me/s/v2ray24",
    "https://t.me/s/v2ray2_ng",
    "https://t.me/s/v2ray4win",
    "https://t.me/s/v2ray60",
    "https://t.me/s/v2ray666",
    "https://t.me/s/v2ray851403",
    "https://t.me/s/v2ray_83",
    "https://t.me/s/V2ray_Alpha",
    "https://t.me/s/v2ray_ar",
    "https://t.me/s/v2ray_best_iran",
    "https://t.me/s/v2ray_best_server",
    "https://t.me/s/v2ray_cartel",
    "https://t.me/s/v2ray_config_2023",
    "https://t.me/s/v2ray_configs_pool",
    "https://t.me/s/v2ray_custom",
    "https://t.me/s/v2ray_donya",
    "https://t.me/s/v2ray_fark",
    "https://t.me/s/v2ray_fd",
    "https://t.me/s/v2ray_for_free",
    "https://t.me/s/v2ray_free_conf",
    "https://t.me/s/V2Ray_FreedomIran",
    "https://t.me/s/v2ray_gh",
    "https://t.me/s/v2ray_god",
    "https://t.me/s/v2ray_he",
    "https://t.me/s/v2ray_inter",
    "https://t.me/s/v2ray_iran88",
    "https://t.me/s/v2ray_ka",
    "https://t.me/s/v2ray_majani",
    "https://t.me/s/v2ray_melli",
    "https://t.me/s/v2ray_n",
    "https://t.me/s/v2ray_napster_vpn",
    "https://t.me/s/V2RAY_NEW",
    "https://t.me/s/v2ray_ng",
    "https://t.me/s/v2ray_ng_vip",
    "https://t.me/s/v2ray_npv1",
    "https://t.me/s/v2ray_official",
    "https://t.me/s/v2ray_one1",
    "https://t.me/s/v2ray_only_free",
    "https://t.me/s/v2ray_outlineir",
    "https://t.me/s/v2ray_raha",
    "https://t.me/s/v2ray_reality_new",
    "https://t.me/s/v2ray_rh",
    "https://t.me/s/v2ray_rolly",
    "https://t.me/s/v2ray_seven",
    "https://t.me/s/v2ray_shop_2",
    "https://t.me/s/v2ray_shopb",
    "https://t.me/s/v2ray_sos",
    "https://t.me/s/v2ray_sub",
    "https://t.me/s/v2ray_swhil",
    "https://t.me/s/v2ray_team",
    "https://t.me/s/v2ray_txshop",
    "https://t.me/s/v2ray_ty",
    "https://t.me/s/v2ray_v_vpn",
    "https://t.me/s/v2ray_vemo",
    "https://t.me/s/v2ray_vmes",
    "https://t.me/s/V2RAY_VMESS_free",
    "https://t.me/s/v2ray_vpn_ir",
    "https://t.me/s/v2ray_vpna",
    "https://t.me/s/v2ray_vpnalfa",
    "https://t.me/s/v2ray_youtube",
    "https://t.me/s/v2rayalivpn",
    "https://t.me/s/v2rayan",
    "https://t.me/s/v2rayang201",
    "https://t.me/s/v2rayargon",
    "https://t.me/s/v2rayarmy",
    "https://t.me/s/v2rayaz",
    "https://t.me/s/v2raybaz",
    "https://t.me/s/v2raybe",
    "https://t.me/s/v2raybest1",
    "https://t.me/s/v2raybuddiesvpn",
    "https://t.me/s/v2raybx",
    "https://t.me/s/v2raycg",
    "https://t.me/s/v2raych",
    "https://t.me/s/v2raychanel",
    "https://t.me/s/v2RayChannel",
    "https://t.me/s/v2rayclubs",
    "https://t.me/s/V2rayCollectorDonate",
    "https://t.me/s/v2rayconfigamir",
    "https://t.me/s/v2raycrow",
    "https://t.me/s/v2raydiyako",
    "https://t.me/s/v2rayeservers",
    "https://t.me/s/v2rayexpress",
    "https://t.me/s/v2rayfa",
    "https://t.me/s/v2rayfast",
    "https://t.me/s/v2rayfastone",
    "https://t.me/s/v2rayfr",
    "https://t.me/s/v2rayfree",
    "https://t.me/s/v2rayfree1",
    "https://t.me/s/v2rayfree_server",
    "https://t.me/s/v2rayfreo",
    "https://t.me/s/v2rayhp",
    "https://t.me/s/v2rayhubvip",
    "https://t.me/s/V2rayi_net",
    "https://t.me/s/v2raying",
    "https://t.me/s/v2rayir1",
    "https://t.me/s/v2raykaktusvpn",
    "https://t.me/s/v2rayland02",
    "https://t.me/s/v2raylandd",
    "https://t.me/s/v2rayliberty",
    "https://t.me/s/v2raymastermind",
    "https://t.me/s/v2rayminer",
    "https://t.me/s/v2rayn2g",
    "https://t.me/s/v2rayn5",
    "https://t.me/s/v2rayn_config",
    "https://t.me/s/V2rayN_Free",
    "https://t.me/s/v2rayn_openavpn",
    "https://t.me/s/v2rayn_server",
    "https://t.me/s/v2rayng0051",
    "https://t.me/s/v2rayng01",
    "https://t.me/s/v2rayng110n",
    "https://t.me/s/v2rayng12023",
    "https://t.me/s/v2rayng14",
    "https://t.me/s/v2rayng1ran",
    "https://t.me/s/v2rayng20000",
    "https://t.me/s/v2rayng20000000",
    "https://t.me/s/V2rayNG3",
    "https://t.me/s/v2rayng89",
    "https://t.me/s/v2rayng_13",
    "https://t.me/s/v2rayng_1378",
    "https://t.me/s/v2rayng_147",
    "https://t.me/s/v2rayng_25",
    "https://t.me/s/v2rayng_aads",
    "https://t.me/s/v2rayng_aadss2",
    "https://t.me/s/v2rayng_account_free",
    "https://t.me/s/v2rayng_active",
    "https://t.me/s/v2rayng_anti",
    "https://t.me/s/v2rayng_bit",
    "https://t.me/s/v2rayng_blue",
    "https://t.me/s/v2rayng_canfig1",
    "https://t.me/s/v2rayng_channel",
    "https://t.me/s/v2rayng_channel_vpn",
    "https://t.me/s/v2rayng_city",
    "https://t.me/s/v2rayng_config_amin",
    "https://t.me/s/v2rayng_confiings",
    "https://t.me/s/v2rayng_confings",
    "https://t.me/s/v2rayng_coonfig",
    "https://t.me/s/v2rayng_cooonfig",
    "https://t.me/s/v2rayng_daily",
    "https://t.me/s/v2rayng_fa2",
    "https://t.me/s/v2rayng_fast",
    "https://t.me/s/v2rayng_free",
    "https://t.me/s/v2rayng_galaxy",
    "https://t.me/s/v2rayng_ge",
    "https://t.me/s/v2rayng_klng",
    "https://t.me/s/v2rayng_lion",
    "https://t.me/s/v2rayng_madam",
    "https://t.me/s/v2rayNG_Matsuri",
    "https://t.me/s/v2rayng_my2",
    "https://t.me/s/v2rayng_n2",
    "https://t.me/s/v2rayng_napesternetv",
    "https://t.me/s/v2rayng_nv",
    "https://t.me/s/v2rayng_nv1",
    "https://t.me/s/v2rayng_nvvpn",
    "https://t.me/s/v2rayng_o",
    "https://t.me/s/v2rayng_oorg",
    "https://t.me/s/v2rayng_org",
    "https://t.me/s/v2rayng_outline_vpn",
    "https://t.me/s/v2rayng_outlinee",
    "https://t.me/s/v2rayng_ribvar",
    "https://t.me/s/v2rayng_sell",
    "https://t.me/s/v2rayng_serveer1",
    "https://t.me/s/v2rayng_serverr1",
    "https://t.me/s/v2rayng_uk",
    "https://t.me/s/v2rayng_v",
    "https://t.me/s/v2rayng_v2_ray",
    "https://t.me/s/v2rayNG_VPN",
    "https://t.me/s/v2rayNG_VPNN",
    "https://t.me/s/v2rayng_vpnorg",
    "https://t.me/s/v2rayng_vpnrog",
    "https://t.me/s/v2rayng_vpnt",
    "https://t.me/s/v2rayngalpha",
    "https://t.me/s/v2rayngalphagamer",
    "https://t.me/s/v2rayngb",
    "https://t.me/s/v2rayngc",
    "https://t.me/s/v2rayngchaannel",
    "https://t.me/s/v2rayngchannelll",
    "https://t.me/s/v2rayngcloud",
    "https://t.me/s/v2rayngconfig",
    "https://t.me/s/v2rayngconfiig",
    "https://t.me/s/v2rayngconfings",
    "https://t.me/s/v2rayngfast",
    "https://t.me/s/v2rayngfiree",
    "https://t.me/s/v2rayngfreee",
    "https://t.me/s/v2rayNgg_iran",
    "https://t.me/s/v2rayngim",
    "https://t.me/s/v2rayngmat",
    "https://t.me/s/v2rayngmdd",
    "https://t.me/s/v2rayngn",
    "https://t.me/s/v2rayngnet",
    "https://t.me/s/v2rayngninja",
    "https://t.me/s/v2rayngraisi",
    "https://t.me/s/v2rayngrit",
    "https://t.me/s/v2rayngrr13",
    "https://t.me/s/v2rayngseven",
    "https://t.me/s/v2rayngte",
    "https://t.me/s/v2rayngup",
    "https://t.me/s/v2rayngv",
    "https://t.me/s/v2rayngvp",
    "https://t.me/s/v2rayngvpn",
    "https://t.me/s/v2rayngvpn_1",
    "https://t.me/s/V2rayNGvpni",
    "https://t.me/s/v2rayngvpnl",
    "https://t.me/s/v2rayngvpnn",
    "https://t.me/s/v2rayngvvpn",
    "https://t.me/s/v2rayngw",
    "https://t.me/s/V2rayNGX",
    "https://t.me/s/v2rayninja",
    "https://t.me/s/v2raynselling",
    "https://t.me/s/v2raynz",
    "https://t.me/s/v2rayo7ybv67i76",
    "https://t.me/s/v2rayopen",
    "https://t.me/s/v2rayorng",
    "https://t.me/s/V2RayOxygen",
    "https://t.me/s/v2rayp1",
    "https://t.me/s/v2rayping",
    "https://t.me/s/v2rayport",
    "https://t.me/s/v2rayprooo",
    "https://t.me/s/v2rayprotocol",
    "https://t.me/s/v2rayproxy",
    "https://t.me/s/v2rayrb6",
    "https://t.me/s/v2rayrg",
    "https://t.me/s/v2rayroad",
    "https://t.me/s/v2rayroz",
    "https://t.me/s/v2rayry",
    "https://t.me/s/v2rayserver2023",
    "https://t.me/s/v2rayservere",
    "https://t.me/s/v2rayseven",
    "https://t.me/s/V2raysFree",
    "https://t.me/s/v2rayshop_m",
    "https://t.me/s/v2raysiran",
    "https://t.me/s/v2rayspeed",
    "https://t.me/s/v2raystudents",
    "https://t.me/s/v2raytel",
    "https://t.me/s/v2raytork",
    "https://t.me/s/v2rayturbo",
    "https://t.me/s/V2RayTz",
    "https://t.me/s/v2rayvl",
    "https://t.me/s/v2rayvlp",
    "https://t.me/s/v2rayvmess",
    "https://t.me/s/v2rayvpn009",
    "https://t.me/s/v2rayvpn2",
    "https://t.me/s/v2rayvpnchannel",
    "https://t.me/s/v2rayvpnclub",
    "https://t.me/s/v2rayvx",
    "https://t.me/s/v2rayweb",
    "https://t.me/s/v2rayxd",
    "https://t.me/s/v2rayxservers",
    "https://t.me/s/v2rayy_napsternetv",
    "https://t.me/s/v2rayy_vpn13",
    "https://t.me/s/v2rayyngvpn",
    "https://t.me/s/v2rayza",
    "https://t.me/s/v2rayzone",
    "https://t.me/s/v2raz",
    "https://t.me/s/v2ret",
    "https://t.me/s/v2rez",
    "https://t.me/s/v2rfa",
    "https://t.me/s/v2rng_free1",
    "https://t.me/s/v2royns",
    "https://t.me/s/v2rplus",
    "https://t.me/s/v2rray1_ng",
    "https://t.me/s/v2rray_ng",
    "https://t.me/s/v2ry_proxy",
    "https://t.me/s/v2ryng0",
    "https://t.me/s/v2ryng01",
    "https://t.me/s/v2ryngfree",
    "https://t.me/s/v2ryvip",
    "https://t.me/s/v2safe",
    "https://t.me/s/v2servers1",
    "https://t.me/s/v2sezar",
    "https://t.me/s/v2shop2",
    "https://t.me/s/v2source",
    "https://t.me/s/v2starvip",
    "https://t.me/s/v2teamvip",
    "https://t.me/s/v2turbo",
    "https://t.me/s/v2xsy",
    "https://t.me/s/v3410ray",
    "https://t.me/s/v5ray_ng",
    "https://t.me/s/v_2r_ay",
    "https://t.me/s/v_2ra_y",
    "https://t.me/s/v_2ray1",
    "https://t.me/s/v_2rayng0",
    "https://t.me/s/v_2rayngvpn",
    "https://t.me/s/V_2rey",
    "https://t.me/s/vaiking_vpn",
    "https://t.me/s/Vaslchi_VPN",
    "https://t.me/s/vboxpanel",
    "https://t.me/s/vc_proxy",
    "https://t.me/s/vein_vpn",
    "https://t.me/s/veta_land",
    "https://t.me/s/vezzevpn",
    "https://t.me/s/vip_fragment_v2ray",
    "https://t.me/s/vip_free_vpn02",
    "https://t.me/s/vip_freevpn1",
    "https://t.me/s/vip_tunel",
    "https://t.me/s/vip_vpn_2022",
    "https://t.me/s/vipfastspeed",
    "https://t.me/s/vipmsv2raynp",
    "https://t.me/s/vipnetmeli",
    "https://t.me/s/vipserverstm",
    "https://t.me/s/vipufovpn",
    "https://t.me/s/vipv2rayngnp",
    "https://t.me/s/vipv2rayngvip",
    "https://t.me/s/vipv2rayvip",
    "https://t.me/s/vipv2rey",
    "https://t.me/s/ViPVpn_v2ray",
    "https://t.me/s/vipvpncenter",
    "https://t.me/s/vipvpnsia",
    "https://t.me/s/ViraV2ray",
    "https://t.me/s/vistav2ray",
    "https://t.me/s/vlees_v2rayng",
    "https://t.me/s/vless1",
    "https://t.me/s/vless_vmess",
    "https://t.me/s/vlessconfig",
    "https://t.me/s/vlessh",
    "https://t.me/s/vmesc",
    "https://t.me/s/vmess_freee",
    "https://t.me/s/vmess_ir",
    "https://t.me/s/vmess_iran",
    "https://t.me/s/vmess_vless_v2rayng",
    "https://t.me/s/vmessiran",
    "https://t.me/s/vmessiranproxy",
    "https://t.me/s/vmesskhodam",
    "https://t.me/s/vmessorg",
    "https://t.me/s/VmessProtocol",
    "https://t.me/s/vmessq",
    "https://t.me/s/vmessraygan",
    "https://t.me/s/vmessx",
    "https://t.me/s/VorTexIRN",
    "https://t.me/s/vp22ray",
    "https://t.me/s/vp_n1",
    "https://t.me/s/vpean",
    "https://t.me/s/vpidiamond",
    "https://t.me/s/vplusking",
    "https://t.me/s/vplusvpn_free",
    "https://t.me/s/vpn4ir_1",
    "https://t.me/s/vpn_315",
    "https://t.me/s/VPN_443",
    "https://t.me/s/vpn_accounti",
    "https://t.me/s/vpn_amo",
    "https://t.me/s/vpn_arta",
    "https://t.me/s/vpn_bal0uch",
    "https://t.me/s/vpn_bist1",
    "https://t.me/s/vpn_bu",
    "https://t.me/s/vpn_cck",
    "https://t.me/s/vpn_connect",
    "https://t.me/s/vpn_darkk",
    "https://t.me/s/vpn_famous",
    "https://t.me/s/vpn_ioss",
    "https://t.me/s/vpn_kadeh_iran",
    "https://t.me/s/vpn_land_official",
    "https://t.me/s/vpn_mikey",
    "https://t.me/s/vpn_mikey5",
    "https://t.me/s/vpn_Nv1",
    "https://t.me/s/vpn_ocean",
    "https://t.me/s/vpn_proxy_custom",
    "https://t.me/s/vpn_proxy_v2ry",
    "https://t.me/s/VPN_SOLVE",
    "https://t.me/s/vpn_storm",
    "https://t.me/s/vpn_sts",
    "https://t.me/s/vpn_tehran",
    "https://t.me/s/vpn_v24",
    "https://t.me/s/vpn_v2a",
    "https://t.me/s/vpn_v2ra_ng",
    "https://t.me/s/vpn_v2ray_v2",
    "https://t.me/s/vpn_v2ray_wireguard",
    "https://t.me/s/vpn_v2rayng_iran",
    "https://t.me/s/vpn_xw",
    "https://t.me/s/vpn_zvpn",
    "https://t.me/s/vpnafra",
    "https://t.me/s/vpnaiden",
    "https://t.me/s/vpnamohelp",
    "https://t.me/s/vpnandroid2",
    "https://t.me/s/vpnbigbang",
    "https://t.me/s/vpncaneel",
    "https://t.me/s/vpnclick",
    "https://t.me/s/vpnclop",
    "https://t.me/s/vpnconfignet",
    "https://t.me/s/vpncostume",
    "https://t.me/s/vpncostumer",
    "https://t.me/s/VPNCUSTOMIZE",
    "https://t.me/s/vpned",
    "https://t.me/s/vpnepic",
    "https://t.me/s/vpneti",
    "https://t.me/s/vpnfail_v2ray",
    "https://t.me/s/vpnfastservice",
    "https://t.me/s/vpnforsale1402",
    "https://t.me/s/vpnfree",
    "https://t.me/s/vpnfree6",
    "https://t.me/s/vpnfree85",
    "https://t.me/s/vpnfreeaccounts",
    "https://t.me/s/vpnfreeo",
    "https://t.me/s/vpnfreesec",
    "https://t.me/s/vpngate_config",
    "https://t.me/s/vpnhomeiran",
    "https://t.me/s/vpnhouse_official",
    "https://t.me/s/vpnhub69",
    "https://t.me/s/vpnhubmarket",
    "https://t.me/s/vpnia1",
    "https://t.me/s/vpnkafing",
    "https://t.me/s/vpnkanfik",
    "https://t.me/s/vpnkaro",
    "https://t.me/s/vpnmasi",
    "https://t.me/s/vpnmeg",
    "https://t.me/s/vpnmega1",
    "https://t.me/s/vpnmk1",
    "https://t.me/s/vpnod",
    "https://t.me/s/vpnowl",
    "https://t.me/s/vpnpacket",
    "https://t.me/s/vpnplus100",
    "https://t.me/s/vpnplusee_free",
    "https://t.me/s/vpnpopular2023",
    "https://t.me/s/vpnprivet",
    "https://t.me/s/vpnpro_xy",
    "https://t.me/s/vpnprosec",
    "https://t.me/s/VpnProsecc",
    "https://t.me/s/vpnradin",
    "https://t.me/s/vpnserver_tel",
    "https://t.me/s/vpnservergprc",
    "https://t.me/s/vpnserverrr",
    "https://t.me/s/vpnsgod",
    "https://t.me/s/vpnshecan",
    "https://t.me/s/vpnskyy",
    "https://t.me/s/vpnsshocean",
    "https://t.me/s/vpnstable",
    "https://t.me/s/vpnstorefast",
    "https://t.me/s/vpnsupportfast",
    "https://t.me/s/vpntrt",
    "https://t.me/s/vpntwitt",
    "https://t.me/s/vpnv2rayng90",
    "https://t.me/s/vpnv2rayngv",
    "https://t.me/s/vpnv2rayonline",
    "https://t.me/s/vpnv2raytop",
    "https://t.me/s/vpnvg",
    "https://t.me/s/VPNwedbaz",
    "https://t.me/s/vpnwlf",
    "https://t.me/s/vpnworldone",
    "https://t.me/s/vpnx1x",
    "https://t.me/s/vpnyes",
    "https://t.me/s/vpnzamin",
    "https://t.me/s/vpnzzo",
    "https://t.me/s/vpra_org",
    "https://t.me/s/vpray3",
    "https://t.me/s/vrayhub",
    "https://t.me/s/vruntech",
    "https://t.me/s/vtolink",
    "https://t.me/s/vtworay_wolf",
    "https://t.me/s/wancloudfa",
    "https://t.me/s/wangcai_8",
    "https://t.me/s/wbrovers",
    "https://t.me/s/wearestand",
    "https://t.me/s/webhube",
    "https://t.me/s/webonim",
    "https://t.me/s/webovpn",
    "https://t.me/s/webshecan",
    "https://t.me/s/wedbazvpn",
    "https://t.me/s/weepeen",
    "https://t.me/s/whale8",
    "https://t.me/s/whalevpnchannel",
    "https://t.me/s/wirepro_vpn",
    "https://t.me/s/wmessorg",
    "https://t.me/s/wolf_vpn02",
    "https://t.me/s/womanlifefreedom13",
    "https://t.me/s/womanlifefreedomvpn",
    "https://t.me/s/world_vmess",
    "https://t.me/s/worldprooxy",
    "https://t.me/s/wsbvpn",
    "https://t.me/s/wxdy666",
    "https://t.me/s/wxgmrjdcc",
    "https://t.me/s/x2ray_team",
    "https://t.me/s/x4azadi",
    "https://t.me/s/x_her0",
    "https://t.me/s/x_n_v2ray_g_x",
    "https://t.me/s/xiaoxinv",
    "https://t.me/s/xiv2ray",
    "https://t.me/s/xivpn",
    "https://t.me/s/xnxv2ray",
    "https://t.me/s/XpnTeam",
    "https://t.me/s/xrayproxy",
    "https://t.me/s/xrayzxn",
    "https://t.me/s/xsv2ray",
    "https://t.me/s/xsvpn_ch",
    "https://t.me/s/xv2ray_ng",
    "https://t.me/s/xvproxy",
    "https://t.me/s/xyzquantvpn",
    "https://t.me/s/yaney_01",
    "https://t.me/s/yarito_media",
    "https://t.me/s/yaritovpn",
    "https://t.me/s/yasv2ray",
    "https://t.me/s/yekoyekvpn",
    "https://t.me/s/ytte3la",
    "https://t.me/s/yunbaitech",
    "https://t.me/s/yuproxytelegram",
    "https://t.me/s/yushik_vpn",
    "https://t.me/s/yxjnode",
    "https://t.me/s/zapasv2ray",
    "https://t.me/s/zar_vpn",
    "https://t.me/s/zayn_vpn",
    "https://t.me/s/zdyz2",
    "https://t.me/s/zed_vpn",
    "https://t.me/s/zedmodeontech",
    "https://t.me/s/zedping",
    "https://t.me/s/zen_cloud",
    "https://t.me/s/zeptovpn",
    "https://t.me/s/zeroshop00",
    "https://t.me/s/zerov2shop",
    "https://t.me/s/zibanabz",
    "https://t.me/s/zilatvpn",
    "https://t.me/s/zilv2ray_service",
    "https://t.me/s/ztv2ray",
    "https://t.me/s/zvpnn",
    "https://t.me/s/zyfxlnn",
    "https://t.me/s/nim_vpn_ir",
    "https://t.me/s/outline_vpn",
    "https://t.me/s/hope_net",
    "https://t.me/s/proxystore11",
    "https://t.me/s/yaney_01",
    "https://t.me/s/fnet00",
    "https://t.me/s/azadnet",
    "https://t.me/s/customv2ray",
]
TELEGRAM_URLs = sorted( set( TELEGRAM_URLs ), key = str.casefold )

###############################################################################
SUPPORTED_FANQIANG_PROTOCALs = [
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
SUPPORTED_FANQIANG_PROTOCALs = sorted( set( SUPPORTED_FANQIANG_PROTOCALs ), key = str.casefold )

###############################################################################
PRESENT_DNSs = {}

###############################################################################

#### CHECK IPV4/IPV6 ####################################################### {{
# https://gist.githubusercontent.com/dfee/6ed3a4b05cfe7a6faf40a2102408d5d8/raw/9a6e81e7b4cd0d092c62d70ea1c8016f1b56b706/ip_regex.py
# Constructed with help from
#    http://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
#    Try it on regex101: https://regex101.com/r/yVdrJQ/1
IPV4SEG  = r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
IPV4ADDR = r'(?:(?:' + IPV4SEG + r'\.){3,3}' + IPV4SEG + r')'
IPV6SEG  = r'(?:(?:[0-9a-fA-F]){1,4})'
IPV6GROUPS = (
    r'(?:' + IPV6SEG + r':){7,7}' + IPV6SEG,                  # 1:2:3:4:5:6:7:8
    r'(?:' + IPV6SEG + r':){1,7}:',                           # 1::                                 1:2:3:4:5:6:7::
    r'(?:' + IPV6SEG + r':){1,6}:' + IPV6SEG,                 # 1::8               1:2:3:4:5:6::8   1:2:3:4:5:6::8
    r'(?:' + IPV6SEG + r':){1,5}(?::' + IPV6SEG + r'){1,2}',  # 1::7:8             1:2:3:4:5::7:8   1:2:3:4:5::8
    r'(?:' + IPV6SEG + r':){1,4}(?::' + IPV6SEG + r'){1,3}',  # 1::6:7:8           1:2:3:4::6:7:8   1:2:3:4::8
    r'(?:' + IPV6SEG + r':){1,3}(?::' + IPV6SEG + r'){1,4}',  # 1::5:6:7:8         1:2:3::5:6:7:8   1:2:3::8
    r'(?:' + IPV6SEG + r':){1,2}(?::' + IPV6SEG + r'){1,5}',  # 1::4:5:6:7:8       1:2::4:5:6:7:8   1:2::8
    IPV6SEG + r':(?:(?::' + IPV6SEG + r'){1,6})',             # 1::3:4:5:6:7:8     1::3:4:5:6:7:8   1::8
    r':(?:(?::' + IPV6SEG + r'){1,7}|:)',                     # ::2:3:4:5:6:7:8    ::2:3:4:5:6:7:8  ::8       ::
    r'fe80:(?::' + IPV6SEG + r'){0,4}%[0-9a-zA-Z]{1,}',       # fe80::7:8%eth0     fe80::7:8%1  (link-local IPv6 addresses with zone index)
    r'::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]' + IPV4ADDR,     # ::255.255.255.255  ::ffff:255.255.255.255  ::ffff:0:255.255.255.255 (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r'(?:' + IPV6SEG + r':){1,4}:[^\s:]' + IPV4ADDR,          # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
)
IPV6ADDR = '|'.join(['(?:{})'.format(g) for g in IPV6GROUPS[::-1]])  # Reverse rows for greedy match
############################################################################ }}

GEO_DB_PATH = 'GeoLite2-City.mmdb'

###############################################################################
if __name__ == "__main__":
    current_filename = os.path.basename(__file__)

    logging.basicConfig(filename=f'{current_filename}.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    #### Tee assist ############################ {{
    # https://www.google.com/search?q=python+print+to+tee
    # Save the original standard error and open a new log file to track only errors.
    save_original_stderr = sys.stderr #  sys.__stderr__
    errlog_file = open(f'{current_filename}.track.err', 'w', encoding='utf-8')
    # Redirect sys.stderr to the Tee class
    sys.stderr = Tee(save_original_stderr, errlog_file)
    ############################################ }}
    # Data Stream:
    #    Python --> MyPrintErr --> { stderr --> Tee[save_stderr/original_stderr, errlog_file], logging }

    main()

################################## END ########################################

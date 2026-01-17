###############################################################################
# https://github.com/Epodonios/bulk-xray-v2ray-vless-vmess-...-configs/blob/main/main.py
from bs4 import BeautifulSoup, NavigableString, Tag
from datetime import datetime, timedelta, timezone
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
import hashlib
import inspect
import ipaddress
import json
import lzma
import os
import os.path
import re
import requests
import shutil
import socket
import sys
import tempfile
import time
import urllib.parse
import zipfile

###############################################################################
def main():
    #### Preparation of environment variables #############################
    __func__ = inspect.currentframe().f_code.co_name
    __script_name__ = os.path.basename(__file__)

    #### Global variables that are referenced #####
    global TELEGRAM_URLs
    global SUPPORTED_FANQIANG_PROTOCALs
    global PRESENT_DNSs
    global IPV6ADDR
    global GEO_DB_PATH

    #{{{ Parameter preparation via getopt {{{{{{{{{
    bRedownload = False
    sDnsServer = '8.8.8.8'
    nDnsMaxSurvivalMinutes = 30
    sDnsMaxSurvivalMinutes = '30'

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hrd:g:t:", ["help", "redownload", "dnsserver", "geo_db_path", "dns_max_survival_minutes" ])

    except getopt.GetoptError:
        print(f'Usage: {__script_name__} -r<redownload> -d <dnsserver> -g <geo_db_path> -t <dns_max_survival_minutes>')
        sys.exit(2)

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
            print(f'Usage: {__script_name__} -r<redownload> -d <dnsserver> -g <geo_db_path> -t <dns_max_survival_minutes>')
            sys.exit(3)
    #}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}

    if not is_valid_ip( sDnsServer ):
        print( f"The specified dnsserver parameter '{sDnsServer}' is not an IP address." )
        sys.exit(4)

    if not sDnsMaxSurvivalMinutes.isdigit():
        print( f"The specified dns_max_survival_minutes parameter '{sDnsMaxSurvivalMinutes}' is not a number." )
        sys.exit(5)
    nDnsMaxSurvivalMinutes = int(sDnsMaxSurvivalMinutes)
    if nDnsMaxSurvivalMinutes < 0:
        print( f"The dns_max_survival_minutes parameter '{nDnsMaxSurvivalMinutes}' cannot be less than zero." )
        sys.exit(4)

    if not os.path.exists(GEO_DB_PATH):
        print( f"The specified IP map file '{GEO_DB_PATH}' does not exist." )
        sys.exit(6)

    #### Preparation of environment variables 2 ###
    __script_dir__ = Path(__file__).resolve().parent
    __web_download_dir__ = f"{__script_dir__}/Epodonios/downloads"
    __Ford_assembly_line__ = f"{__script_dir__}/Epodonios/Fordline"
    F = f"{__Ford_assembly_line__}/"
    __timestamp_str__ = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #### Redirect print to logfile ################
    original_stdout = sys.stdout
    log_file = open(f'{__script_name__}.log', 'a', encoding='utf-8')
    sys.stdout = Tee(original_stdout, log_file)

    #### Check system environment #################
    bFirstRun = False
    if not os.path.exists(__web_download_dir__):
        bFirstRun = True
        os.makedirs(__web_download_dir__)
    if not Path(__web_download_dir__).exists():
        print(f"{__func__}(): Folder '{__web_download_dir__}' dose NOT exist.")
        sys.exit(7)
    #----------------------------------------------------------------------
    if not os.path.exists(__Ford_assembly_line__):
        bFirstRun = True
        os.makedirs(__Ford_assembly_line__)
    if not Path(__Ford_assembly_line__).exists():
        print(f"{__func__}(): Folder '{__Ford_assembly_line__}' dose NOT exist.")
        sys.exit(8)

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

        shutil_compress( zip_root_dir, backupzip )

        assert os.path.exists( zip_root_dir ) and os.path.isdir( zip_root_dir )
        #try:
        #    shutil.rmtree( zip_root_dir )
        #except Exception as e:
        #    print( f"Deleting directory '{zip_root_dir}' failed: {e}" )
        #    sys.exit(9)

    #### Do you want to skip the download? ########
    if bRedownload:
        download(TELEGRAM_URLs, __web_download_dir__, f"{F}a.list_downloaded_file.txt")
        filter_acceptable_files( f"{F}a.list_downloaded_file.txt", f"{F}b.accept_file.txt", f"{F}c.dead_link.txt", 7 )

    if not os.path.exists(f"{F}b.accept_file.txt"):
        print("Please use the -r option to download first.")
        sys.exit(10)

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
    with open(f"{F}1.data_incomplete.txt", 'r', encoding='utf-8') as f, open(f"{F}2.data_incomplete.txt", 'w', encoding='utf-8') as f2:
        for line in f:
            cleaned_line = line.strip()
            if all_double_fslash.match(cleaned_line):
                f2.write(cleaned_line + "\n")

    #### Split a row containing information about multiple nodes into rows where each node occupies a separate row.
    with open(f"{F}2.data_incomplete.txt", 'r', encoding='utf-8') as f, open(f"{F}3.data_incomplete.txt", 'w', encoding='utf-8') as f2:
        for line in f:
            protocals = copy.deepcopy( SUPPORTED_FANQIANG_PROTOCALs )
            protocals.append( "http://" )
            protocals.append( "https://" )
            nodes = split_nodes( line, protocals )
            f2.writelines( "\n".join( nodes ) )

    sort_and_unique_file_lines(f"{F}3.data_incomplete.txt", f"{F}4.data_incomplete.txt")

    remove_unsupported_protocols(f"{F}4.data_incomplete.txt", f"{F}5.data_incomplete.txt", SUPPORTED_FANQIANG_PROTOCALs )

    with open(f"{F}5.data_incomplete.txt", 'r', encoding='utf-8') as f, open(f"{F}6.data_incomplete.txt", 'w', encoding='utf-8') as f2, open(f"{F}d.urls_where_host_extraction_failed.txt", 'w', encoding='utf-8') as f3:
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
        f.close

    with open(f"{F}6.data_incomplete.txt", 'r', encoding='utf-8') as f, open(f"{F}7.data_incomplete.txt", 'w', encoding='utf-8') as f2:
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
                    ips = dns_lookup_with_specific_server(domain, '8.8.8.8')
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
        create_sub_section()
        print("Configs saved successfully.")
    else:
        print("No V2Ray configs found.")

    with open("present_dns.json", "w") as f:
        json.dump(PRESENT_DNSs, f, indent=4) # 'indent=4' makes the file human-readable

    # To restore original behavior and close the file
    sys.stdout = original_stdout
    log_file.close()

###############################################################################
###############################################################################
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
                print(f"{__func__}(): Failed to fetch URL (Status Code: {response.status_code})")
                continue
            filename=extract_filename_from_url(url)
            with open(f"{web_download_folder}/{filename}.html.tmp", "w", encoding="utf-8") as f:
                f.write(response.text)
                fList.write( f"{url},{web_download_folder}/{filename}.html.tmp,{web_download_folder}/{filename}.html\n" )
                success_count +=1
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
    fList.close()
    session.close()
    return success_count

###############################################################################
def filter_acceptable_files( list_downloaded_fpath, list_accept_fpath, list_dead_links, no_changes_in_days ):
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
                except FileNotFoundError:
                    print(f"{__func__}(): File not found.")
                except FileExistsError:
                    print(f"{__func__}(): New file name already exists.")
                except PermissionError:
                    print(f"{__func__}(): Permission denied. Unable to rename the file.")
                except Exception as e:
                    print(f"{__func__}(): An unexpected error occurred during processing: {e}")

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
        print(f"{__func__}(): An exception other than a value error occurred: {e}")
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
    except dns.resolver.LifetimeTimeout:
        print(f"{__func__}(): Resolve '{domain_name}' exception -- DNS server '{dns_server_ip}' timed out.")
        return None
    #except dns.resolver.NXDOMAIN as e:
    #    print(f"{__func__}(): Resolve '{domain_name}' exception -- The DNS query name does not exist. Details: {e}")
    #    return None
    #except dns.resolver.NoNameservers as e:
    #    print(f"{__func__}(): Resolve '{domain_name}' exception -- All nameservers failed to answer the query. Details: {e}")
    #    return None
    except Exception as e:
        print(f"{__func__}(): Resolve '{domain_name}' exception. Details: {e}")
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
def extract_all_v2ray_links( htmlfile, days_ago, protocals ):
    __func__ = inspect.currentframe().f_code.co_name

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
        print(f"{__func__}(): An exception occurred when file '{input_filename}' was opened for reading.")
        return

    # Convert the set to a list and sort it
    sorted_unique_lines = sorted(list(unique_lines))

    try:
        # Write the sorted unique lines to a new file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.writelines(line + '\n' for line in sorted_unique_lines)
    except Exception as e:
        print(f"{__func__}(): An exception occurred when file '{output_filename}' was opened for writing.")
        return

###############################################################################
def remove_unsupported_protocols( input_filename, output_filename, protocals ):
    __func__ = inspect.currentframe().f_code.co_name
    try:
        with open(input_filename, 'r', encoding='utf-8') as f, open(output_filename, 'w', encoding='utf-8') as f2:
            for line in f:
                for item in protocals:
                    if line.startswith(item):
                        f2.write(line)
    except Exception as e:
        print(f"{__func__}(): An error occurred during processing: {e}")

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
            json_string = decoded_string;
        except Exception as e:
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
                print(f"{__func__}(): An unexpected error occurred by Jsondecode(\"{json_string.strip()}\"): {e}")
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
    except geoip2.errors.AddressNotFoundError:
        print(f"{__func__}(): Location for IP {ip[0]} not found in the database.")
    except Exception as e:
        print(f"{__func__}(): An error occurred: {e}")
    return None

###############################################################################
def open_file_to_read_if_recent(file_path, max_minutes=30):
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
        print(f"An error occurred: {e}")

###############################################################################
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
    "https://t.me/s/tg233boy"           ,
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
#------------------------------------------------------------------------------
# Constructed with help from
# http://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
# Try it on regex101: https://regex101.com/r/yVdrJQ/1

#------- TEST CASE / EXAMPLE, PART 1 ------------------------------------------
#   import re

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

#------- TEST CASE / EXAMPLE, PART 2 ------------------------------------------
#   tests = [
#       '1::',
#       '1:2:3:4:5:6:7::',
#       '1::8',
#       '1:2:3:4:5:6::8',
#       '1:2:3:4:5:6::8',
#       '1::7:8',
#       '1:2:3:4:5::7:8',
#       '1:2:3:4:5::8',
#       '1::6:7:8',
#       '1:2:3:4::6:7:8',
#       '1:2:3:4::8',
#       '1::5:6:7:8',
#       '1:2:3::5:6:7:8',
#       '1:2:3::8',
#       '1::4:5:6:7:8',
#       '1:2::4:5:6:7:8',
#       '1:2::8',
#       '1::3:4:5:6:7:8',
#       '1::3:4:5:6:7:8',
#       '1::8',
#       '::2:3:4:5:6:7:8',
#       '::2:3:4:5:6:7:8',
#       '::8',
#       '::',
#       'fe80::7:8%eth0',
#       'fe80::7:8%1',
#       '::255.255.255.255',
#       '::ffff:255.255.255.255',
#       '::ffff:0:255.255.255.255',
#       '2001:db8:3:4::192.0.2.33',
#       '64:ff9b::192.0.2.33',
#   ]
#
#   # IPV6ADDR Tests
#   def test_individual(tests):
#       for t in tests:
#           assert re.search(IPV6ADDR, t).group() == t
#
#   # MULTILINE
#   def test_multiline(tests):
#       _tests = tests[:]
#       for t in re.findall(IPV6ADDR, ' '.join(tests)):
#           _tests.remove(t)
#       assert not _tests
#
#   test_individual(tests)
#   test_multiline(tests)
#
#   log_data = "Server started at 2001:db8::1:1:1:1:1, connection from 192.168.1.1, another ipv6: fe80::8329"
#   aIpv6 = re.findall(IPV6ADDR, log_data)
#   print(aIpv6)
#   aIpv4 = re.findall(IPV4ADDR, log_data)
#   print(aIpv4)
#}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}} }}

GEO_DB_PATH = 'GeoLite2-City.mmdb'

###############################################################################
if __name__ == "__main__":
    main()

################################## END ########################################

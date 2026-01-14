###############################################################################
# https://github.com/Epodonios/bulk-xray-v2ray-vless-vmess-...-configs/blob/main/main.py
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import os
import shutil
from datetime import datetime
import urllib.parse
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
import tempfile
import hashlib
import os.path

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
def get_v2ray_links(session, name, url):
    try:
        response = session.get(url, timeout=5)
        if response.status_code == 200:
            temp_file_path=""
            # Use NamedTemporaryFile as a context manager
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.html', prefix=f'{name}') as temp_file:
                # Get the name/path of the temporary file
                temp_file_path = temp_file.name

                # You can write to the file
                temp_file.write(response.content)
                temp_file.flush() # Ensure data is written to disk

                # The file remains on disk even after the 'with' block,
                # because delete is set to False

            #if os.path.isfile(temp_file_path):
            #    sha256_hash = hashlib.sha256(temp_file_path)

            #soup = BeautifulSoup(response.content, 'html.parser')

            for br in soup.find_all("br"):
                br.replace_with("\n")

            #codes = soup.find_all('code')
            #span = soup.find_all('span')
            #div = soup.find_all('div')
            #pre = soup.find_all('pre')
            #blockquote = soup.find_all('blockquote')

            #all_tags = codes + span + div + pre + blockquote
            all_tags = soup.find_all()

            v2ray_configs = []
            for tag in all_tags:
                text = tag.get_text()
                if False                                     \
                  or text.lower().startswith('vmess://')     \
                  or text.lower().startswith('vless://')     \
                  or text.lower().startswith('ss://')        \
                  or text.lower().startswith('ssr://')       \
                  or text.lower().startswith('trojan://')    \
                  or text.lower().startswith('tuic://')      \
                  or text.lower().startswith('hysteria://')  \
                  or text.lower().startswith('hy2://')       \
                  or text.lower().startswith('socks5://')    \
                  or text.lower().startswith('warp://')      \
                  or text.lower().startswith('wireguard://') \
                  or text.lower().startswith('snell://')     \
                  or text.lower().startswith('tuic://')      \
                  or text.lower().startswith('ssh://')       \
                  or text.lower().startswith('mieru://')     \
                  or text.lower().startswith('sudoku://')    \
                  :
                    v2ray_configs.append(text)

            return v2ray_configs
        else:
            print(f"Failed to fetch URL (Status Code: {response.status_code})")
            return None

    except HTTPError as e:
        print(f"HTTP error occurred: {e}") # e.g., 404 Not Found, 500 Internal Server Error
    except ConnectionError as e:
        print(f"Connection error occurred: {e}") # e.g., DNS failure, refused connection, no internet
    except Timeout as e:
        print(f"Timeout error occurred: {e}") # Request took too long to respond
    except RequestException as e:
        # Catch any other general requests error that inherits from RequestException
        print(f"An unexpected request error occurred: {e}")
    except Exception as e:
        # Catch any other potential errors (e.g., issues with Beautiful Soup parsing)
        print(f"An unexpected error occurred during processing: {e}")
    else:
        # Code to run if the try block completes successfully (no exceptions)
        print("All steps completed without critical errors.")
    return None

###############################################################################
def sort_and_unique_file_lines(input_filename, output_filename):
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
    except FileNotFoundError:
        print(f"Error: {input_filename} not found.")
        return

    # Convert the set to a list and sort it
    sorted_unique_lines = sorted(list(unique_lines))

    # Write the sorted unique lines to a new file
    with open(output_filename, 'w') as f_out:
        f_out.writelines(sorted_unique_lines)

    print(f"Processed lines from '{input_filename}' and saved to '{output_filename}'.")

###############################################################################
def get_region_from_ip(session, ip):
    api_endpoints = [
        f'https://ipapi.co/{ip}/json/',
        f'https://ipwhois.app/json/{ip}',
        f'http://www.geoplugin.net/json.gp?ip={ip}',
        f'https://api.ipbase.com/v1/json/{ip}'
    ]

    for endpoint in api_endpoints:
        try:
            response = session.get(endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    if 'country' in data:
                        print(data['country'])
                        return data['country']
        except Exception as e:
            print(f"Error retrieving region from {endpoint}: {e}")
    return None

###############################################################################
def save_configs_by_region(session, configs):
    config_folder = "sub"
    if os.path.exists(config_folder):
        for folder in os.listdir(config_folder):
            folder_path = os.path.join(config_folder, folder)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)

    if not os.path.exists(config_folder):
        os.makedirs(config_folder)

    for config in configs:
        ip = config.split('//')[1].split('/')[0]
        print(ip+"++++++++++++++++++++++++++++++++++")
        region = get_region_from_ip(session, ip)
        if region:
            region_folder = os.path.join(config_folder, region)
            if not os.path.exists(region_folder):
                os.makedirs(region_folder)

            with open(os.path.join(region_folder, 'config.txt'), 'a', encoding='utf-8') as file:
                file.write(config + '\n')

###############################################################################
def create_sub_section():
    readme_path = "README.md"
    sub_folder = "sub"
    found_sub_section = False

    content=""
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as readme_file:
            content = readme_file.read()

            if '## Sub' in content:
                found_sub_section = True

    new_content = ""
    new_content += "## Sub\n"
    new_content += "| Sub |\n"
    new_content += "|-----|\n"

    for root, dirs, files in os.walk(sub_folder):
        for directory in dirs:
            config_path = os.path.join(root, directory, 'config.txt')
            if os.path.exists(config_path):
                url = f"https://raw.githubusercontent.com/Epodonios/bulk-xray-v2ray-vless-vmess-...-configs/main/sub/{urllib.parse.quote(directory)}/config.txt"
                new_content += f"| [{directory}]({url}) |\n"

    with open(readme_path, 'w', encoding='utf-8') as readme_file:
        if found_sub_section:
            readme_file.write(content.replace(content[content.find('## Sub'):content.find('\n\n', content.find('## Sub'))], new_content))
        else:
            readme_file.write(content + new_content)

###############################################################################
if __name__ == "__main__":

    current_filename = os.path.basename(__file__)

    # Save original stdout
    original_stdout = sys.stdout

    # Open a log file
    log_file = open(f'{current_filename}.log', 'a')

    # Redirect sys.stdout to the custom Tee object
    sys.stdout = Tee(original_stdout, log_file)

    telegram_urls = [
        "Tele.v2line.html              , https://t.me/s/v2line",
        "Tele.forwardv2ray.html        , https://t.me/s/forwardv2ray",
        "Tele.inikotesla.html          , https://t.me/s/inikotesla",
        "Tele.PrivateVPNs.html         , https://t.me/s/PrivateVPNs",
        "Tele.VlessConfig.html         , https://t.me/s/VlessConfig",
        "Tele.V2pedia.html             , https://t.me/s/V2pedia",
        "Tele.v2rayNG_Matsuri.html     , https://t.me/s/v2rayNG_Matsuri",
        "Tele.PrivateVPNs.html         , https://t.me/s/PrivateVPNs",
        "Tele.proxystore11.html        , https://t.me/s/proxystore11",
        "Tele.DirectVPN.html           , https://t.me/s/DirectVPN",
        "Tele.VmessProtocol.html       , https://t.me/s/VmessProtocol",
        "Tele.OutlineVpnOfficial.html  , https://t.me/s/OutlineVpnOfficial",
        "Tele.networknim.html          , https://t.me/s/networknim",
        "Tele.beiten.html              , https://t.me/s/beiten",
        "Tele.MsV2ray.html             , https://t.me/s/MsV2ray",
        "Tele.foxrayiran.html          , https://t.me/s/foxrayiran",
        "Tele.DailyV2RY.html           , https://t.me/s/DailyV2RY",
        "Tele.yaney_01.html            , https://t.me/s/yaney_01",
        "Tele.FreakConfig.html         , https://t.me/s/FreakConfig",
        "Tele.EliV2ray.html            , https://t.me/s/EliV2ray",
        "Tele.ServerNett.html          , https://t.me/s/ServerNett",
        "Tele.proxystore11.html        , https://t.me/s/proxystore11",
        "Tele.v2rayng_fa2.html         , https://t.me/s/v2rayng_fa2",
        "Tele.v2rayng_org.html         , https://t.me/s/v2rayng_org",
        "Tele.V2rayNGvpni.html         , https://t.me/s/V2rayNGvpni",
        "Tele.custom_14.html           , https://t.me/s/custom_14",
        "Tele.v2rayNG_VPNN.html        , https://t.me/s/v2rayNG_VPNN",
        "Tele.v2ray_outlineir.html     , https://t.me/s/v2ray_outlineir",
        "Tele.v2_vmess.html            , https://t.me/s/v2_vmess",
        "Tele.FreeVlessVpn.html        , https://t.me/s/FreeVlessVpn",
        "Tele.vmess_vless_v2rayng.html , https://t.me/s/vmess_vless_v2rayng",
        "Tele.PrivateVPNs.html         , https://t.me/s/PrivateVPNs",
        "Tele.freeland8.html           , https://t.me/s/freeland8",
        "Tele.vmessiran.html           , https://t.me/s/vmessiran",
        "Tele.Outline_Vpn.html         , https://t.me/s/Outline_Vpn",
        "Tele.vmessq.html              , https://t.me/s/vmessq",
        "Tele.WeePeeN.html             , https://t.me/s/WeePeeN",
        "Tele.V2rayNG3.html            , https://t.me/s/V2rayNG3",
        "Tele.ShadowsocksM.html        , https://t.me/s/ShadowsocksM",
        "Tele.shadowsocksshop.html     , https://t.me/s/shadowsocksshop",
        "Tele.v2rayan.html             , https://t.me/s/v2rayan",
        "Tele.ShadowSocks_s.html       , https://t.me/s/ShadowSocks_s",
        "Tele.VmessProtocol.html       , https://t.me/s/VmessProtocol",
        "Tele.napsternetv_config.html  , https://t.me/s/napsternetv_config",
        "Tele.Easy_Free_VPN.html       , https://t.me/s/Easy_Free_VPN",
        "Tele.V2Ray_FreedomIran.html   , https://t.me/s/V2Ray_FreedomIran",
        "Tele.V2RAY_VMESS_free.html    , https://t.me/s/V2RAY_VMESS_free",
        "Tele.v2ray_for_free.html      , https://t.me/s/v2ray_for_free",
        "Tele.V2rayN_Free.html         , https://t.me/s/V2rayN_Free",
        "Tele.free4allVPN.html         , https://t.me/s/free4allVPN",
        "Tele.vpn_ocean.html           , https://t.me/s/vpn_ocean",
        "Tele.configV2rayForFree.html  , https://t.me/s/configV2rayForFree",
        "Tele.FreeV2rays.html          , https://t.me/s/FreeV2rays",
        "Tele.DigiV2ray.html           , https://t.me/s/DigiV2ray",
        "Tele.v2rayNG_VPN.html         , https://t.me/s/v2rayNG_VPN",
        "Tele.freev2rayssr.html        , https://t.me/s/freev2rayssr",
        "Tele.v2rayn_server.html       , https://t.me/s/v2rayn_server",
        "Tele.Shadowlinkserverr.html   , https://t.me/s/Shadowlinkserverr",
        "Tele.iranvpnet.html           , https://t.me/s/iranvpnet",
        "Tele.vmess_iran.html          , https://t.me/s/vmess_iran",
        "Tele.mahsaamoon1.html         , https://t.me/s/mahsaamoon1",
        "Tele.V2RAY_NEW.html           , https://t.me/s/V2RAY_NEW",
        "Tele.v2RayChannel.html        , https://t.me/s/v2RayChannel",
        "Tele.configV2rayNG.html       , https://t.me/s/configV2rayNG",
        "Tele.config_v2ray.html        , https://t.me/s/config_v2ray",
        "Tele.vpn_proxy_custom.html    , https://t.me/s/vpn_proxy_custom",
        "Tele.vpnmasi.html             , https://t.me/s/vpnmasi",
        "Tele.v2ray_custom.html        , https://t.me/s/v2ray_custom",
        "Tele.VPNCUSTOMIZE.html        , https://t.me/s/VPNCUSTOMIZE",
        "Tele.HTTPCustomLand.html      , https://t.me/s/HTTPCustomLand",
        "Tele.vpn_proxy_custom.html    , https://t.me/s/vpn_proxy_custom",
        "Tele.ViPVpn_v2ray.html        , https://t.me/s/ViPVpn_v2ray",
        "Tele.FreeNet1500.html         , https://t.me/s/FreeNet1500",
        "Tele.v2ray_ar.html            , https://t.me/s/v2ray_ar",
        "Tele.beta_v2ray.html          , https://t.me/s/beta_v2ray",
        "Tele.vip_vpn_2022.html        , https://t.me/s/vip_vpn_2022",
        "Tele.FOX_VPN66.html           , https://t.me/s/FOX_VPN66",
        "Tele.VorTexIRN.html           , https://t.me/s/VorTexIRN",
        "Tele.YtTe3la.html             , https://t.me/s/YtTe3la",
        "Tele.V2RayOxygen.html         , https://t.me/s/V2RayOxygen",
        "Tele.Network_442.html         , https://t.me/s/Network_442",
        "Tele.VPN_443.html             , https://t.me/s/VPN_443",
        "Tele.v2rayng_v.html           , https://t.me/s/v2rayng_v",
        "Tele.ultrasurf_12.html        , https://t.me/s/ultrasurf_12",
        "Tele.iSeqaro.html             , https://t.me/s/iSeqaro",
        "Tele.frev2rayng.html          , https://t.me/s/frev2rayng",
        "Tele.frev2ray.html            , https://t.me/s/frev2ray",
        "Tele.FreakConfig.html         , https://t.me/s/FreakConfig",
        "Tele.Awlix_ir.html            , https://t.me/s/Awlix_ir",
        "Tele.v2rayngvpn.html          , https://t.me/s/v2rayngvpn",
        "Tele.God_CONFIG.html          , https://t.me/s/God_CONFIG",
        "Tele.Configforvpn01.html      , https://t.me/s/Configforvpn01",
    ]


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

    all_v2ray_configs = []
    for Channel in telegram_urls:
        parts=Channel.split(",")
        name=parts[0].strip()
        url=parts[1].strip()
        print(f"{url}")
        v2ray_configs = get_v2ray_links(session, url)
        if v2ray_configs:
            all_v2ray_configs.extend(v2ray_configs)

    f=open("alltags.txt", 'w')
    print(all_v2ray_configs,file=f)
    f.close()

    f=open("bulk-xray.txt", 'w')
    for cfg in all_v2ray_configs:
        print(cfg,file=f)
    f.close()

    valid = re.compile(".*://.*")
    with open("bulk-xray.txt", 'r') as f, open("bulk-xray2.txt", 'w') as f2:
        # Iterate through each line in the file
        for line in f:
            # Optional: Use strip() to remove leading/trailing whitespace, including the newline character
            cleaned_line = line.strip()
            if valid.match(cleaned_line):
                f2.write(cleaned_line+"\n")

    f.close()
    f2.close()

    sort_and_unique_file_lines("bulk-xray2.txt","bulk-xray3.txt")

#if all_v2ray_configs:
    #    save_configs_by_region(session, all_v2ray_configs)
    #    create_sub_section()
    #    print("Configs saved successfully.")
    #else:
    #    print("No V2Ray configs found.")

    # To restore original behavior and close the file
    sys.stdout = original_stdout
    log_file.close()
    session.close()

################################## END ########################################






























































































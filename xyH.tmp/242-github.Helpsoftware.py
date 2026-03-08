###############################################################################
# https://zhuanlan.zhihu.com/p/546788844
from bs4 import BeautifulSoup, NavigableString, Tag
from datetime import datetime
from io import StringIO
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
def getTagsBetween( soup, star_tag_string, end_tag_string ):
    start_tag = soup.find('p', string=star_tag_string)
    if not start_tag:
        MyPrintErr(f"Tag (\'p\', string=\'{star_tag_string}\') NOT exist.")
        sys.exit(1)
    end_tag = soup.find('p', string=end_tag_string)
    if not end_tag:
        MyPrintErr(f"Tag (\'p\', string=\'{end_tag_string}\') NOT exist.")
        sys.exit(1)

    tags_between = []
    current_element = start_tag.next_sibling

    while current_element and current_element != end_tag:
        # Check if the element is an actual tag and not just a newline or whitespace
        if isinstance(current_element, Tag):
            tags_between.append(current_element)
        # You can also collect NavigableString if you want raw text
        # elif isinstance(current_element, NavigableString) and current_element.strip():
        #     tags_between.append(current_element.strip())

        current_element = current_element.next_sibling

    tags='<ppp>'
    for tag in tags_between:
        tags+=str(tag)
    tags+='</ppp>'
    return tags

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
    response = session.get(input_url, timeout=5)
    if response.status_code != 200:
        MyPrintErr(f"The response.status.code of webpage \"{input_url}\" return {response.status_code}.")

    #<p dir="auto">一、节点订阅地址(直接复制链接地址粘贴到订阅地址里即可)</p>
    #<p dir="auto">(一)SSR免费节点订阅地址</p>
    #<p dir="auto"><a href="https://www.liesauer.net/yogurt/subscribe?ACCESS_TOKEN=DAYxR3mMaZAsaqUb" rel="nofollow">https://www.liesauer.net/yogurt/subscribe?ACCESS_TOKEN=DAYxR3mMaZAsaqUb</a></p>
    #<p dir="auto"><a href="https://nodes.fanqiang.network/pubconfig/wei6krXcNqyho1b8" rel="nofollow">https://nodes.fanqiang.network/pubconfig/wei6krXcNqyho1b8</a></p>
    #<p dir="auto">(二)v2ray免费节点订阅地址</p>
    #<p dir="auto"><a href="https://www.xrayvip.com/free.txt" rel="nofollow">https://www.xrayvip.com/free.txt</a></p>
    #<p dir="auto"><a href="https://github.com/StormragerCN/v2ray/raw/refs/heads/main/v2ray">https://github.com/StormragerCN/v2ray/raw/refs/heads/main/v2ray</a></p>
    #<p dir="auto"><a href="https://github.com/ermaozi/get_subscribe/raw/refs/heads/main/subscribe/v2ray.txt">https://github.com/ermaozi/get_subscribe/raw/refs/heads/main/subscribe/v2ray.txt</a></p>
    #<p dir="auto">(三)Clash免费节点订阅地址</p>
    #<p dir="auto"><a href="https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/c.yaml" rel="nofollow">https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/c.yaml</a></p>
    #<p dir="auto"><a href="https://github.com/aiboboxx/clashfree/blob/main/clash.yml">https://github.com/aiboboxx/clashfree/blob/main/clash.yml</a></p>
    #<p dir="auto"><a href="https://gcore.jsdelivr.net/gh/aiboboxx/clashfree@refs/heads/main/clash.yml" rel="nofollow">https://gcore.jsdelivr.net/gh/aiboboxx/clashfree@refs/heads/main/clash.yml</a></p>
    #<p dir="auto"><a href="https://cdn.jsdelivr.net/gh/vxiaov/free_proxies@main/clash/clash.provider.yaml" rel="nofollow">https://cdn.jsdelivr.net/gh/vxiaov/free_proxies@main/clash/clash.provider.yaml</a>
    #(使用CDN链接,有延迟)</p>
    #<p dir="auto"><a href="https://raw.githubusercontent.com/vxiaov/free_proxies/main/clash/clash.provider.yaml" rel="nofollow">https://raw.githubusercontent.com/vxiaov/free_proxies/main/clash/clash.provider.yaml</a>
    #(原地址，需要通过代理访问)</p>
    #<p dir="auto"><a href="https://github.com/ermaozi/get_subscribe/raw/refs/heads/main/subscribe/clash.yml">https://github.com/ermaozi/get_subscribe/raw/refs/heads/main/subscribe/clash.yml</a></p>
    #<p dir="auto"><a href="https://github.com/anaer/Sub/raw/refs/heads/main/clash.yaml">https://github.com/anaer/Sub/raw/refs/heads/main/clash.yaml</a></p>
    #<p dir="auto"><a href="https://www.xrayvip.com/free.yaml" rel="nofollow">https://www.xrayvip.com/free.yaml</a></p>
    #<p dir="auto"><a href="https://github.com/aiboboxx/clashfree/raw/refs/heads/main/clash.yml">https://github.com/aiboboxx/clashfree/raw/refs/heads/main/clash.yml</a></p>
    #<p dir="auto">(四)通用免费节点订阅地址</p>
    #<p dir="auto"><a href="https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt" rel="nofollow">https://raw.githubusercontent.com/free18/v2ray/refs/heads/main/v.txt</a></p>
    #<p dir="auto"><a href="https://proxy.v2gh.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub" rel="nofollow">https://proxy.v2gh.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub</a></p>
    #<p dir="auto">或（<a href="https://mirror.v2gh.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub%EF%BC%89" rel="nofollow">https://mirror.v2gh.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub）</a></p>
    #<p dir="auto"><a href="https://hyt-allen-xu.netlify.app" rel="nofollow">https://hyt-allen-xu.netlify.app</a></p>
    #<p dir="auto"><a href="https://github.com/Jsnzkpg/Jsnzkpg/raw/refs/heads/Jsnzkpg/Jsnzkpg">https://github.com/Jsnzkpg/Jsnzkpg/raw/refs/heads/Jsnzkpg/Jsnzkpg</a></p>
    #<p dir="auto">二、免费节点网址（需要自己去网站里找）</p>
    #<p dir="auto">网站1：<a href="https://www.youneed.win/category/nodeshare" rel="nofollow">https://www.youneed.win/category/nodeshare</a>
    #（有ss节点、vmess节点、vless节点、trojan节点、hysteria2节点等）</p>
    #<p dir="auto">网站2：<a href="https://github.com/aiboboxx/v2rayfree">https://github.com/aiboboxx/v2rayfree</a>
    #（有ss节点、vmess节点、vless节点、trojan节点、hysteria2节点等）</p>
    #<p dir="auto">网站3：<a href="https://fanqiang.network/" rel="nofollow">https://fanqiang.network/</a></p>
    #<p dir="auto">网站4：<a href="https://github.com/Alvin9999/new-pac/wiki/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7">https://github.com/Alvin9999/new-pac/wiki/ss%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7</a>
    #（主要是SS节点）</p>
    #<p dir="auto">网站5：<a href="https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7">https://github.com/Alvin9999/new-pac/wiki/v2ray%E5%85%8D%E8%B4%B9%E8%B4%A6%E5%8F%B7</a>
    #（主要是vless、vmess节点）</p>
    #<p dir="auto">网站6：<a href="https://github.com/aiboboxx/clashfree">https://github.com/aiboboxx/clashfree</a>
    #（clash节点分享）</p>
    #<p dir="auto">网站7：<a href="https://free-ss.site/" rel="nofollow">https://free-ss.site/</a>
    #（用手机app扫描识别二维码导入vless节点，目前有2个节点，账号1每天08:00更新，账号2每天20:00更新）</p>
    #<p dir="auto">网站8：<a href="https://free.datiya.com/" rel="nofollow">https://free.datiya.com/</a>
    #（含Clash订阅地址和V2ray订阅地址）</p>
    #<p dir="auto">网站9：<a href="https://github.com/mksshare/mksshare.github.io">https://github.com/mksshare/mksshare.github.io</a>
    #（分享Clash、v2rayN、iOS小火箭订阅链接）</p>
    #<p dir="auto">三、分享proxy代理IP科学上网（我没用过所以不知道能不能用，自己进去找）</p>
    #<p dir="auto"><a href="https://premproxy.com/list/" rel="nofollow">https://premproxy.com/list/</a></p>
    #<p dir="auto"><a href="https://spys.one/en/" rel="nofollow">https://spys.one/en/</a></p>
    #<p dir="auto"><a href="https://www.freeproxy.world/" rel="nofollow">https://www.freeproxy.world/</a></p>
    #<p dir="auto"><a href="https://github.com/free18/v2ray">https://github.com/free18/v2ray</a></p>
    #<p dir="auto">四、分享节点的telegram群组</p>
    #<p dir="auto"><a href="https://t.me/byxiaoxi" rel="nofollow">https://t.me/byxiaoxi</a></p>
    #<p dir="auto"><a href="https://t.me/ssList" rel="nofollow">https://t.me/ssList</a></p>
    #<p dir="auto"><a href="https://t.me/V2List" rel="nofollow">https://t.me/V2List</a></p>
    #<p dir="auto"><a href="https://t.me/youneedproxy" rel="nofollow">https://t.me/youneedproxy</a></p>
    #<p dir="auto"><a href="https://t.me/s/v2raydailyupdate" rel="nofollow">https://t.me/s/v2raydailyupdate</a></p>
    #<p dir="auto"><a href="https://t.me/vvkj11" rel="nofollow">https://t.me/vvkj11</a></p>
    #<p dir="auto"><a href="https://t.me/v2ray3" rel="nofollow">https://t.me/v2ray3</a></p>
    #<p dir="auto"><a href="https://t.me/shadowrocket_android" rel="nofollow">https://t.me/shadowrocket_android</a></p>
    #<p dir="auto"><a href="https://t.me/freenodedaily" rel="nofollow">https://t.me/freenodedaily</a></p>
    #<p dir="auto"><a href="https://t.me/SSRSUB" rel="nofollow">https://t.me/SSRSUB</a></p>
    #<p dir="auto"><a href="https://t.me/ShadowsocksRssr" rel="nofollow">https://t.me/ShadowsocksRssr</a></p>
    #<p dir="auto"><a href="https://t.me/ssrList" rel="nofollow">https://t.me/ssrList</a></p>
    #<p dir="auto"><a href="https://t.me/freeshadowsock" rel="nofollow">https://t.me/freeshadowsock</a></p>
    #<p dir="auto"><a href="https://t.me/socks5list" rel="nofollow">https://t.me/socks5list</a> （这个是TG代理）</p>
    #<p dir="auto"><a href="https://t.me/ssrshares" rel="nofollow">https://t.me/ssrshares</a></p>
    #<p dir="auto"><a href="https://t.me/onessr" rel="nofollow">https://t.me/onessr</a></p>
    #<p dir="auto"><a href="https://t.me/baipiaojiedian" rel="nofollow">https://t.me/baipiaojiedian</a></p>
    #<p dir="auto"><a href="https://t.me/ShareCentre" rel="nofollow">https://t.me/ShareCentre</a></p>
    #<p dir="auto"><a href="https://t.me/share_proxy_001" rel="nofollow">https://t.me/share_proxy_001</a></p>
    #<p dir="auto"><a href="https://t.me/xrayfree" rel="nofollow">https://t.me/xrayfree</a></p>
    #<p dir="auto">五、其它
    #<a href="https://shadowshare.v2cross.com/" rel="nofollow">https://shadowshare.v2cross.com/</a>
    #这是一个手机软件（安卓和ios客户端），ShadowShare是一款共享节点app，我们每天都会对所有的共享节点进行测试，选取高质量的节点给大家使用。反正网站写着永远提供免费服务，不知道怎么样，有兴趣自行尝试，个人不做任何背书。</p>
    #<p dir="auto">内容来源：内容都是网上搜集，不保证一定可用。
    #另外注意请不要相信任何广告，理性看待事物，自觉提高甄辨和防骗能力。</p>

    ##################################################################
    soup=BeautifulSoup(response.text, 'html.parser')
    tags = getTagsBetween( soup, "一、节点订阅地址(直接复制链接地址粘贴到订阅地址里即可)", "二、免费节点网址（需要自己去网站里找）" )
    soup=BeautifulSoup(tags, 'html.parser')
    v2rayNodes=soup.find_all(lambda tag: tag.name=='a' and tag.has_attr('href') and tag['href']==tag.get_text() and tag.parent.name=='p')
    f=open(output_nodes_file, 'w')
    for node in v2rayNodes:
        nodesInfo=node['href']
        if nodesInfo:
            print(nodesInfo,file=f)
    f.close()

    ##################################################################
    soup=BeautifulSoup(response.text, 'html.parser')
    tags = getTagsBetween( soup, "二、免费节点网址（需要自己去网站里找）", "三、分享proxy代理IP科学上网（我没用过所以不知道能不能用，自己进去找）" )
    soup=BeautifulSoup(tags, 'html.parser')
    v2rayNodes=soup.find_all(lambda tag: tag.name=='a' and tag.has_attr('href') and tag['href']==tag.get_text() and tag.parent.name=='p')
    f=open(output_nodes_file, 'a')
    for node in v2rayNodes:
        nodesInfo=node['href']
        if nodesInfo:
            nodesInfo+=',Multi_level_analysis_is_required'
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

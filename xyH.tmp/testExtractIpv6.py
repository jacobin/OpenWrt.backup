#### case 1 ###################################################################
#    import ipaddress
#    import re
#
#    def extract_ipv6_addresses(text):
#        ipv6_list = []
#        # This is a basic pattern for potential IP parts, not a full validator
#        # It looks for sequences of hex digits and colons
#        #potential_ips = re.findall(r'[0-9a-fA-F:]+', text)
#        #potential_ips = re.findall(r'\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:)))(%.+)?\s*', text)
#        potential_ips = re.findall(r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))', text)
#        for potential_ip in potential_ips:
#            try:
#                # Try to create an IPv6 address object
#                ip = ipaddress.ip_address(potential_ip)
#                if isinstance(ip, ipaddress.IPv6Address):
#                    ipv6_list.append(str(ip))
#            except ValueError:
#                # Not a valid IPv6 address
#                continue
#        return ipv6_list
#
#    log_data = "Server started at 2001:db8::1:1:1:1:1, connection from 192.168.1.1, another ipv6: fe80::8329"
#    found_ipv6s = extract_ipv6_addresses(log_data)
#    print(found_ipv6s)
#    # Output: ['2001:db8::1:1:1:1:1', 'fe80::8329']

#### case 2 ###################################################################
# https://gist.githubusercontent.com/dfee/6ed3a4b05cfe7a6faf40a2102408d5d8/raw/9a6e81e7b4cd0d092c62d70ea1c8016f1b56b706/ip_regex.py
#------------------------------------------------------------------------------
# Constructed with help from
# http://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
# Try it on regex101: https://regex101.com/r/yVdrJQ/1

import re

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


tests = [
    '1::',
    '1:2:3:4:5:6:7::',
    '1::8',
    '1:2:3:4:5:6::8',
    '1:2:3:4:5:6::8',
    '1::7:8',
    '1:2:3:4:5::7:8',
    '1:2:3:4:5::8',
    '1::6:7:8',
    '1:2:3:4::6:7:8',
    '1:2:3:4::8',
    '1::5:6:7:8',
    '1:2:3::5:6:7:8',
    '1:2:3::8',
    '1::4:5:6:7:8',
    '1:2::4:5:6:7:8',
    '1:2::8',
    '1::3:4:5:6:7:8',
    '1::3:4:5:6:7:8',
    '1::8',
    '::2:3:4:5:6:7:8',
    '::2:3:4:5:6:7:8',
    '::8',
    '::',
    'fe80::7:8%eth0',
    'fe80::7:8%1',
    '::255.255.255.255',
    '::ffff:255.255.255.255',
    '::ffff:0:255.255.255.255',
    '2001:db8:3:4::192.0.2.33',
    '64:ff9b::192.0.2.33',
]

# IPV6ADDR Tests
def test_individual(tests):
    for t in tests:
        assert re.search(IPV6ADDR, t).group() == t

# MULTILINE
def test_multiline(tests):
    _tests = tests[:]
    for t in re.findall(IPV6ADDR, ' '.join(tests)):
        _tests.remove(t)
    assert not _tests

test_individual(tests)
test_multiline(tests)

log_data = "Server started at 2001:db8::1:1:1:1:1, connection from 192.168.1.1, another ipv6: fe80::8329"
aaa = re.findall(IPV6ADDR, log_data)
print(aaa)
aaa = re.findall(IPV4ADDR, log_data)
print(aaa)
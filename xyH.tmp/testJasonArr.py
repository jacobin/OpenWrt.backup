import json

with open('bulk-xray-v2ray-vless-vmess-...-configs.telegram_channels.hjson', 'r', encoding='utf-8') as f, open('bulk-xray-v2ray-vless-vmess-...-configs.telegram_channels.json', 'w', encoding='utf-8') as f1:
    for line in f.readlines():
        if not (line.strip().startswith('#')):
            f1.write(line)

with open('bulk-xray-v2ray-vless-vmess-...-configs.telegram_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

print(channels)
"""Unwrap dashboard JSON files from Grafana API format to provisioning format"""
import json, glob

base = r'D:\workbuddyproject\亚伯兰实习\ansible-deploy\roles\grafana\files\dashboards'
for f in glob.glob(base + r'\*.json'):
    with open(f, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    if 'dashboard' in data and isinstance(data['dashboard'], dict):
        data = data['dashboard']
    with open(f, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    print(f'Fixed: {f} -> title={data.get("title","?")}')

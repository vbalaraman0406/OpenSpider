import requests
import json
import re
from datetime import datetime, timedelta

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

# Fetch the Chrome zero-day article from BleepingComputer
try:
    # Try the specific URL pattern for March 2026
    urls = [
        'https://www.bleepingcomputer.com/news/google/google-fixes-two-new-chrome-zero-days-exploited-in-attacks/',
        'https://www.bleepingcomputer.com/news/security/google-fixes-chrome-zero-day-exploited-in-espionage-campaign/',
    ]
    for url in urls:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            text = r.text
            cves = list(set(re.findall(r'CVE-\d{4}-\d{4,}', text)))
            # Extract text content
            from html.parser import HTMLParser
            class TP(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.texts = []
                    self.skip = False
                def handle_starttag(self, t, a):
                    if t in ['script','style']: self.skip = True
                def handle_endtag(self, t):
                    if t in ['script','style']: self.skip = False
                def handle_data(self, d):
                    if not self.skip and d.strip():
                        self.texts.append(d.strip())
            p = TP()
            p.feed(text)
            full = ' '.join(p.texts)
            # Find relevant sentences
            sents = []
            for s in full.split('.'):
                s = s.strip()
                if any(k in s.lower() for k in ['cve-', 'zero-day', 'chrome', 'exploit', 'patch', 'severity', 'critical', 'high']):
                    if len(s) > 20 and len(s) < 300:
                        sents.append(s)
            print(f"URL: {url}")
            print(f"CVEs found: {cves}")
            print(f"Key sentences ({len(sents)}):")
            for s in sents[:20]:
                print(f"  - {s}")
            print("---")
except Exception as e:
    print(f"Error: {e}")

# Also check for Ivanti, Fortinet, or other recent zero-days
try:
    r = requests.get('https://www.bleepingcomputer.com/feed/', headers=headers, timeout=15)
    if r.status_code == 200:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(r.content)
        print("\nBleepingComputer Recent Headlines:")
        for item in root.findall('.//item')[:15]:
            title = item.find('title').text if item.find('title') is not None else ''
            pubdate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            print(f"  [{pubdate[:16]}] {title}")
except Exception as e:
    print(f"RSS Error: {e}")

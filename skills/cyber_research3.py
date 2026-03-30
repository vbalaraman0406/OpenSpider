import requests
import json
from datetime import datetime, timedelta
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
results = {}

# 1. Re-fetch CISA KEV for recent entries
try:
    r = requests.get('https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json', headers=headers, timeout=15)
    if r.status_code == 200:
        data = r.json()
        vulns = data.get('vulnerabilities', [])
        cutoff = datetime.now() - timedelta(days=7)
        recent = []
        for v in vulns:
            try:
                added = datetime.strptime(v.get('dateAdded',''), '%Y-%m-%d')
                if added >= cutoff:
                    recent.append({
                        'cve': v.get('cveID'),
                        'vendor': v.get('vendorProject'),
                        'product': v.get('product'),
                        'name': v.get('vulnerabilityName'),
                        'dateAdded': v.get('dateAdded'),
                        'dueDate': v.get('dueDate'),
                        'action': v.get('requiredAction'),
                        'notes': v.get('notes', '')[:100]
                    })
            except:
                pass
        results['cisa_kev_recent'] = recent
except Exception as e:
    results['cisa_error'] = str(e)

# 2. Fetch BleepingComputer Chrome zero-day article
try:
    r = requests.get('https://www.bleepingcomputer.com/news/google/google-fixes-two-new-chrome-zero-days-exploited-in-attacks/', headers=headers, timeout=15)
    if r.status_code == 200:
        text = r.text
        # Extract CVE IDs
        cves = list(set(re.findall(r'CVE-\d{4}-\d{4,}', text)))
        # Extract key paragraphs
        from html.parser import HTMLParser
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.in_article = False
            def handle_starttag(self, tag, attrs):
                if tag == 'article' or ('class' in dict(attrs) and 'article' in dict(attrs).get('class','')):
                    self.in_article = True
            def handle_data(self, data):
                if data.strip():
                    self.text.append(data.strip())
        parser = TextExtractor()
        parser.feed(text)
        full_text = ' '.join(parser.text)
        # Find sentences with CVE
        sentences = [s.strip() for s in full_text.split('.') if 'CVE' in s or 'zero-day' in s.lower() or 'chrome' in s.lower()][:15]
        results['chrome_zeroday'] = {'cves': cves, 'key_sentences': sentences}
    else:
        results['chrome_error'] = f'Status {r.status_code}'
except Exception as e:
    results['chrome_error'] = str(e)

# 3. Fetch The Hacker News articles for more details
try:
    r = requests.get('https://feeds.feedburner.com/TheHackersNews', headers=headers, timeout=15)
    if r.status_code == 200:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall('.//item')[:25]:
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            desc = item.find('description').text if item.find('description') is not None else ''
            pubdate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            # Get all security articles
            items.append({'title': title, 'link': link, 'date': pubdate[:25], 'desc': desc[:200]})
        results['thn_all'] = items[:15]
except Exception as e:
    results['thn_error'] = str(e)

print(json.dumps(results, indent=2, default=str))

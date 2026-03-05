import requests
from bs4 import BeautifulSoup
import re
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
results = {}

# Try to get SPY price from stockanalysis with different headers
try:
    h2 = headers.copy()
    h2['Accept'] = 'text/html,application/xhtml+xml'
    h2['Accept-Language'] = 'en-US,en;q=0.9'
    r = requests.get('https://stockanalysis.com/etf/spy/', headers=h2, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()[:4000]
    prices = re.findall(r'\$([\d,]+\.\d{2})', text)
    changes = re.findall(r'([+-]?\d+\.\d+%)', text)
    results['SPY'] = {'prices': prices[:8], 'changes': changes[:8], 'snippet': text[:500]}
except Exception as e:
    results['SPY_err'] = str(e)[:200]

# Try to read a news article about Iran-US conflict from a major outlet
try:
    time.sleep(1)
    r = requests.get('https://www.aljazeera.com/tag/iran/', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    headlines = []
    for a in soup.find_all('a'):
        t = a.get_text(strip=True)
        href = a.get('href', '')
        if len(t) > 25 and len(t) < 200 and ('iran' in t.lower() or 'tehran' in t.lower() or 'strait' in t.lower() or 'gulf' in t.lower()):
            headlines.append(t)
    results['aljazeera_iran'] = headlines[:15]
except Exception as e:
    results['aljazeera_err'] = str(e)[:200]

# Try AP News
try:
    time.sleep(1)
    r = requests.get('https://apnews.com/hub/iran', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    headlines = []
    for a in soup.find_all('a'):
        t = a.get_text(strip=True)
        if len(t) > 25 and len(t) < 200:
            headlines.append(t)
    results['ap_iran'] = headlines[:15]
except Exception as e:
    results['ap_err'] = str(e)[:200]

# Try to get Dow Jones from wsj
try:
    time.sleep(1)
    r = requests.get('https://www.wsj.com/market-data', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()[:3000]
    # Look for index values
    idx_prices = re.findall(r'([\d,]+\.\d{2})', text)
    results['wsj_market'] = {'prices': idx_prices[:15], 'snippet': text[:500]}
except Exception as e:
    results['wsj_err'] = str(e)[:200]

print(json.dumps(results, indent=2, default=str))

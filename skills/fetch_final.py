import requests
from bs4 import BeautifulSoup
import re
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
results = {}

# Try stockanalysis.com for defense stocks
defense = {'LMT': 'lmt', 'RTX': 'rtx', 'NOC': 'noc', 'GD': 'gd'}
for ticker, slug in defense.items():
    try:
        time.sleep(1)
        r = requests.get(f'https://stockanalysis.com/stocks/{slug}/', headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text()[:3000]
        # Find price pattern - usually first large number
        prices = re.findall(r'\$([\d,]+\.\d{2})', text)
        changes = re.findall(r'([+-]?\d+\.\d+%)', text)
        results[ticker] = {'prices': prices[:5], 'changes': changes[:5]}
    except Exception as e:
        results[ticker] = {'error': str(e)[:150]}

# S&P 500 from stockanalysis
try:
    time.sleep(1)
    r = requests.get('https://stockanalysis.com/stocks/spy/', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()[:3000]
    prices = re.findall(r'\$([\d,]+\.\d{2})', text)
    changes = re.findall(r'([+-]?\d+\.\d+%)', text)
    results['SPY'] = {'prices': prices[:5], 'changes': changes[:5]}
except Exception as e:
    results['SPY'] = {'error': str(e)[:150]}

# QQQ for NASDAQ
try:
    time.sleep(1)
    r = requests.get('https://stockanalysis.com/stocks/qqq/', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()[:3000]
    prices = re.findall(r'\$([\d,]+\.\d{2})', text)
    changes = re.findall(r'([+-]?\d+\.\d+%)', text)
    results['QQQ'] = {'prices': prices[:5], 'changes': changes[:5]}
except Exception as e:
    results['QQQ'] = {'error': str(e)[:150]}

# Try Bing for Iran war news
try:
    time.sleep(1)
    r = requests.get('https://www.bing.com/search?q=iran+us+war+military+developments+march+2026', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for li in soup.find_all('li', class_='b_algo'):
        h2 = li.find('h2')
        if h2:
            snippets.append(h2.get_text(strip=True))
        p = li.find('p')
        if p:
            snippets.append(p.get_text(strip=True)[:200])
    results['bing_iran'] = snippets[:15]
except Exception as e:
    results['bing_iran_err'] = str(e)[:150]

# Bing for defense stocks performance
try:
    time.sleep(1)
    r = requests.get('https://www.bing.com/search?q=defense+stocks+LMT+RTX+NOC+performance+iran+war+2026', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for li in soup.find_all('li', class_='b_algo'):
        h2 = li.find('h2')
        if h2:
            snippets.append(h2.get_text(strip=True))
        p = li.find('p')
        if p:
            snippets.append(p.get_text(strip=True)[:200])
    results['bing_defense'] = snippets[:10]
except Exception as e:
    results['bing_defense_err'] = str(e)[:150]

# Bing for oil analyst commentary
try:
    time.sleep(1)
    r = requests.get('https://www.bing.com/search?q=oil+price+analyst+forecast+iran+conflict+2026', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for li in soup.find_all('li', class_='b_algo'):
        p = li.find('p')
        if p:
            snippets.append(p.get_text(strip=True)[:200])
    results['bing_oil_analyst'] = snippets[:8]
except Exception as e:
    results['bing_oil_err'] = str(e)[:150]

print(json.dumps(results, indent=2, default=str))
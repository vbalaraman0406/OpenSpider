import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Try Google News RSS for market reactions
print('=== Market Reaction News ===')
try:
    rss_url = 'https://news.google.com/rss/search?q=stock+market+Iran+war+oil+prices&hl=en-US&gl=US&ceid=US:en'
    resp = requests.get(rss_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'xml')
    items = soup.find_all('item')[:8]
    for item in items:
        title = item.find('title').get_text() if item.find('title') else ''
        pub = item.find('pubDate').get_text() if item.find('pubDate') else ''
        print(f'  - [{pub}] {title}')
except Exception as e:
    print(f'  Error: {e}')

# Try to get stock quotes from Yahoo Finance
print('\n=== Stock/Market Data ===')
tickers = {
    'S&P 500': '%5EGSPC',
    'Dow Jones': '%5EDJI',
    'Crude Oil': 'CL%3DF',
    'Gold': 'GC%3DF',
    'LMT': 'LMT',
    'RTX': 'RTX',
    'NOC': 'NOC'
}

for name, ticker in tickers.items():
    try:
        url = f'https://finance.yahoo.com/quote/{ticker}/'
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Try to find price data
        price_el = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
        change_el = soup.find('fin-streamer', {'data-field': 'regularMarketChange'})
        pct_el = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'})
        price = price_el.get_text(strip=True) if price_el else 'N/A'
        change = change_el.get_text(strip=True) if change_el else 'N/A'
        pct = pct_el.get_text(strip=True) if pct_el else 'N/A'
        if price == 'N/A':
            # Try alternate: look for data-value attribute
            price_el2 = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
            if price_el2 and price_el2.has_attr('data-value'):
                price = price_el2['data-value']
        print(f'  {name}: ${price} (Change: {change}, {pct})')
    except Exception as e:
        print(f'  {name}: Error - {e}')

# Also try Google Finance for quick data
print('\n=== Google Finance Fallback ===')
gf_tickers = ['LMT', 'RTX', 'NOC', '.INX', '.DJI']
for t in gf_tickers:
    try:
        url = f'https://www.google.com/finance/quote/{t}:NYSE' if t[0] != '.' else f'https://www.google.com/finance/quote/{t}:INDEXSP' if t == '.INX' else f'https://www.google.com/finance/quote/{t}:INDEXDJX'
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Find price
        price_div = soup.find('div', class_='YMlKec fxKbKc')
        price = price_div.get_text(strip=True) if price_div else 'N/A'
        print(f'  {t}: {price}')
    except Exception as e:
        print(f'  {t}: Error - {e}')

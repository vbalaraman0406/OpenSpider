import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.redfin.com/',
}

# Look up Vancouver WA
for query in ['98682', 'Vancouver WA', '98660']:
    print(f'=== Query: {query} ===')
    lookup = f'https://www.redfin.com/stingray/do/location-autocomplete?location={query}&v=2'
    r = requests.get(lookup, headers=headers, timeout=10)
    t = r.text
    if t.startswith('{}&&'):
        t = t[4:]
    print(repr(t[:800]))
    print()

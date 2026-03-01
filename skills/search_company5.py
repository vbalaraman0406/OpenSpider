import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 1. Try Google search with quotes
print('=== Google Search ===')
try:
    r = requests.get('https://www.google.com/search?q=%22let%27s+remodel%22+bathroom+contractor+vancouver+wa', headers=headers, timeout=10)
    # Extract snippets
    text = re.sub(r'<[^>]+>', ' ', r.text)
    text = re.sub(r'\s+', ' ', text)
    # Find relevant sections
    if 'let' in text.lower() and 'remodel' in text.lower():
        idx = text.lower().find('let')
        print('Found mention:', text[max(0,idx-100):idx+500])
    else:
        print('No mention found. First 1000:', text[:1000])
except Exception as e:
    print(f'Error: {e}')

# 2. Try WA State contractor license lookup
print('\n=== WA State Contractor License ===')
try:
    r = requests.get('https://secure.lni.wa.gov/verify/Results.aspx', params={
        'mode': 'ContractorName',
        'ContractorName': "Let's Remodel",
        'SortColumn': 'ContractorName',
        'SortOrder': 'asc'
    }, headers=headers, timeout=10)
    text = re.sub(r'<[^>]+>', ' ', r.text)
    text = re.sub(r'\s+', ' ', text)
    if 'remodel' in text.lower():
        idx = text.lower().find('remodel')
        print('Found:', text[max(0,idx-200):idx+500])
    else:
        print('No results. Length:', len(text))
        print('First 500:', text[:500])
except Exception as e:
    print(f'Error: {e}')

# 3. Try Facebook search
print('\n=== Facebook Search ===')
try:
    r = requests.get('https://www.facebook.com/search/pages/?q=let%27s%20remodel%20vancouver%20wa', headers=headers, timeout=10)
    text = re.sub(r'<[^>]+>', ' ', r.text)
    text = re.sub(r'\s+', ' ', text)
    if 'remodel' in text.lower():
        idx = text.lower().find('remodel')
        print('Found:', text[max(0,idx-100):idx+500])
    else:
        print('No mention. Length:', len(text))
except Exception as e:
    print(f'Error: {e}')

# 4. Try Bing search
print('\n=== Bing Search ===')
try:
    r = requests.get('https://www.bing.com/search?q=%22let%27s+remodel%22+vancouver+wa+bathroom+contractor', headers=headers, timeout=10)
    text = re.sub(r'<[^>]+>', ' ', r.text)
    text = re.sub(r'\s+', ' ', text)
    if 'remodel' in text.lower():
        idx = text.lower().find('let')
        if idx >= 0:
            print('Found:', text[max(0,idx-50):idx+800])
        else:
            print('Remodel mentioned but no let. First 1000:', text[:1000])
    else:
        print('No mention. First 500:', text[:500])
except Exception as e:
    print(f'Error: {e}')

# 5. Try WA LNI verify API directly
print('\n=== WA LNI Direct API ===')
try:
    r = requests.get('https://secure.lni.wa.gov/verify/', params={
        'mode': 'ContractorName',
        'ContractorName': "Lets Remodel"
    }, headers=headers, timeout=10)
    text = re.sub(r'<[^>]+>', ' ', r.text)
    text = re.sub(r'\s+', ' ', text)
    if 'remodel' in text.lower():
        idx = text.lower().find('remodel')
        print('Found:', text[max(0,idx-200):idx+500])
    else:
        print('No results. First 500:', text[:500])
except Exception as e:
    print(f'Error: {e}')

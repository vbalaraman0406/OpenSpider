import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Get contact page
print('=== CONTACT PAGE ===')
resp = requests.get('https://www.mountainwoodhomes.com/contact/', headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')
text = soup.get_text(separator='\n', strip=True)
lines = [l.strip() for l in text.split('\n') if l.strip()]
for line in lines:
    if any(kw in line.lower() for kw in ['phone', 'tel', 'call', 'email', 'address', 'tigard', 'portland', 'vancouver', '503', '360', 'license', 'ccb', 'bonded', 'insured']):
        print(f'  {line[:200]}')

# Also look for phone in raw HTML
phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]\d{4}', resp.text)
if phones:
    print(f'  Phone numbers found: {set(phones)}')

# Check footer area
print('\n=== FOOTER CONTENT ===')
footer = soup.find('footer')
if footer:
    ft = footer.get_text(separator='\n', strip=True)
    for line in ft.split('\n'):
        line = line.strip()
        if line and len(line) > 3:
            print(f'  {line[:200]}')

# Search for license info on about page
print('\n=== ABOUT PAGE ===')
resp2 = requests.get('https://www.mountainwoodhomes.com/about/', headers=headers, timeout=10)
soup2 = BeautifulSoup(resp2.text, 'html.parser')
text2 = soup2.get_text(separator='\n', strip=True)
lines2 = [l.strip() for l in text2.split('\n') if l.strip()]
for line in lines2:
    if any(kw in line.lower() for kw in ['license', 'ccb', 'bonded', 'insured', 'certified', 'nari', 'member', 'association', 'bbb', 'year', 'founded', 'since', 'experience']):
        print(f'  {line[:250]}')

# Try to get Google rating via search
print('\n=== GOOGLE SEARCH FOR RATING ===')
try:
    resp3 = requests.get('https://www.google.com/search?q=%22Mountainwood+Homes%22+reviews+rating+Portland+OR', headers=headers, timeout=10)
    soup3 = BeautifulSoup(resp3.text, 'html.parser')
    text3 = soup3.get_text(separator='\n', strip=True)
    for line in text3.split('\n'):
        line = line.strip()
        if any(kw in line.lower() for kw in ['review', 'rating', 'star', 'out of', '4.', '5.', 'mountainwood']):
            if len(line) > 3 and len(line) < 300:
                print(f'  {line}')
except Exception as e:
    print(f'  Error: {e}')

# Try GuildQuality page
print('\n=== GUILDQUALITY ===')
try:
    resp4 = requests.get('https://www.guildquality.com/pro/mountainwood-homes', headers=headers, timeout=10)
    if resp4.status_code == 200:
        soup4 = BeautifulSoup(resp4.text, 'html.parser')
        text4 = soup4.get_text(separator='\n', strip=True)
        for line in text4.split('\n'):
            line = line.strip()
            if any(kw in line.lower() for kw in ['rating', 'recommend', 'review', 'score', 'satisfaction', '%']):
                if len(line) > 3 and len(line) < 300:
                    print(f'  {line}')
    else:
        print(f'  Status: {resp4.status_code}')
except Exception as e:
    print(f'  Error: {e}')

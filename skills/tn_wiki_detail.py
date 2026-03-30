import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

def extract_text(html, max_len=5000):
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_len]

url = 'https://en.wikipedia.org/wiki/2026_Tamil_Nadu_Legislative_Assembly_election'
try:
    r = requests.get(url, headers=headers, timeout=15)
    html = r.text
    # Find opinion polls section
    poll_match = re.search(r'Opinion[_ ]polls(.*?)(?:Exit[_ ]polls|Results|See[_ ]also|References)', html, re.DOTALL)
    if poll_match:
        poll_html = poll_match.group(1)
        poll_text = extract_text(poll_html)
        print('OPINION POLLS SECTION:')
        print(poll_text[:3000])
    else:
        print('No opinion polls section found')
    
    # Find parties and alliances section
    party_match = re.search(r'Parties and alliances(.*?)(?:Candidates|Campaign)', html, re.DOTALL)
    if party_match:
        party_html = party_match.group(1)
        party_text = extract_text(party_html)
        print('\nPARTIES AND ALLIANCES:')
        print(party_text[:2000])
    else:
        print('No parties section found')
    
    # Find results section
    results_match = re.search(r'Results by alliance or party(.*?)(?:Results by district|See also|Notes)', html, re.DOTALL)
    if results_match:
        results_html = results_match.group(1)
        results_text = extract_text(results_html)
        print('\nRESULTS BY ALLIANCE/PARTY:')
        print(results_text[:2000])
    else:
        print('No results section found')
except Exception as e:
    print(f'Error: {e}')

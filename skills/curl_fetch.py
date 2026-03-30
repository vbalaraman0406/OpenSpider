import os
import re

# Try using os.popen to run curl
try:
    stream = os.popen('curl -s -L https://www.reuters.com/markets/ -H "User-Agent: Mozilla/5.0"')
    html = stream.read()
    stream.close()
    if html:
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        print('REUTERS:', text[:2000])
    else:
        print('REUTERS: Empty response')
except Exception as e:
    print(f'REUTERS ERROR: {e}')

try:
    stream = os.popen('curl -s -L https://finance.yahoo.com/ -H "User-Agent: Mozilla/5.0"')
    html = stream.read()
    stream.close()
    if html:
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        print('\nYAHOO FINANCE:', text[:2000])
    else:
        print('YAHOO FINANCE: Empty response')
except Exception as e:
    print(f'YAHOO ERROR: {e}')

try:
    stream = os.popen('curl -s -L https://news.ycombinator.com/ -H "User-Agent: Mozilla/5.0"')
    html = stream.read()
    stream.close()
    if html:
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        print('\nHACKER NEWS:', text[:2000])
    else:
        print('HACKER NEWS: Empty response')
except Exception as e:
    print(f'HN ERROR: {e}')

try:
    stream = os.popen('curl -s -L https://apnews.com/ -H "User-Agent: Mozilla/5.0"')
    html = stream.read()
    stream.close()
    if html:
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        print('\nAP NEWS:', text[:2000])
    else:
        print('AP NEWS: Empty response')
except Exception as e:
    print(f'AP ERROR: {e}')

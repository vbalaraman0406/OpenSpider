import json
import re

# Read the saved HTML
with open('redfin_page.html', 'r') as f:
    html = f.read()

print(f'HTML length: {len(html)}')

# Find the ReactServerState InitialContext
match = re.search(r'root\.__reactServerState\.InitialContext\s*=\s*({.*?});\s*(?:</script>|root\.)', html, re.DOTALL)
if match:
    ctx_str = match.group(1)
    print(f'InitialContext length: {len(ctx_str)}')
    
    # This is a large JSON blob. Let's parse it and look for homes data
    try:
        ctx = json.loads(ctx_str)
        # Save parsed context for inspection
        with open('redfin_context.json', 'w') as f:
            json.dump(ctx, f, indent=2)
        
        # Search for homes in the data cache
        cache = ctx.get('ReactServerAgent.cache', {}).get('dataCache', {})
        print(f'Data cache keys: {len(cache)}')
        
        for key in cache:
            val = cache[key]
            resp_body = val.get('responseBody', {})
            if isinstance(resp_body, dict):
                payload = resp_body.get('payload', {})
                if isinstance(payload, dict) and 'homes' in payload:
                    homes = payload['homes']
                    print(f'\nFound homes in cache key: {key[:80]}')
                    print(f'Number of homes: {len(homes)}')
                    
                    # Print first 2 homes structure
                    for i, h in enumerate(homes[:2]):
                        print(f'\nHome {i+1}:')
                        print(json.dumps(h, indent=2)[:600])
    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}')
        # Try to find homes data with simpler regex
        print('\nTrying regex approach on InitialContext...')
        homes_match = re.findall(r'"streetLine"\s*:\s*\{"value"\s*:\s*"([^"]+)"', ctx_str)
        print(f'Found {len(homes_match)} streetLine values: {homes_match[:5]}')
else:
    print('InitialContext not found with primary regex')
    # Try alternative patterns
    match2 = re.search(r'InitialContext\s*=\s*({.*?});', html, re.DOTALL)
    if match2:
        print(f'Found with alt regex, length: {len(match2.group(1))}')
    
    # Try finding homes data directly
    homes_match = re.findall(r'"streetLine"\s*:\s*\{"value"\s*:\s*"([^"]+)"', html)
    print(f'streetLine values in HTML: {homes_match[:10]}')
    
    price_match = re.findall(r'"price"\s*:\s*\{"value"\s*:\s*(\d+)', html)
    print(f'price values in HTML: {price_match[:10]}')

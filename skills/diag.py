import json

with open('/Users/vbalaraman/OpenSpider/workspace/whatsapp_config.json', 'r') as f:
    config = json.load(f)

# Print all top-level keys and their types
for k, v in config.items():
    if isinstance(v, list):
        print(f'{k}: list[{len(v)}]')
        for item in v[:3]:
            print(f'  {json.dumps(item)[:200]}')
    elif isinstance(v, dict):
        print(f'{k}: dict with keys {list(v.keys())[:10]}')
    else:
        print(f'{k}: {json.dumps(v)[:200]}')

print('\n=== FULL CONFIG (truncated) ===')
print(json.dumps(config, indent=2)[:3000])

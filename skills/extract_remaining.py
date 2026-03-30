import json

with open('market_data.json', 'r') as f:
    data = json.load(f)

# Print all defense and energy stock details
for cat in ['Defense', 'Energy']:
    print(f'\n=== {cat} ===')
    for sym, info in data[cat].items():
        for k, v in info.items():
            print(f'  {sym}.{k} = {v}')

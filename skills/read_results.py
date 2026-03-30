import json

with open('tn_election_results.json', 'r') as f:
    d = json.load(f)

for source, data in d.items():
    print(source + ': ' + str(len(data)) + ' items')
    for item in data:
        if isinstance(item, dict):
            print('  - ' + item.get('title', '')[:150])
        else:
            print('  - ' + str(item)[:150])
    print()

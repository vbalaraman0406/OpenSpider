import json

with open('workspace/whatsapp_config.json', 'r') as f:
    config = json.load(f)

if '61423475992' not in config['allowedDMs']:
    config['allowedDMs'].append('61423475992')

with open('workspace/whatsapp_config.json', 'w') as f:
    json.dump(config, f, indent=2)

with open('workspace/whatsapp_config.json', 'r') as f:
    print(f.read())

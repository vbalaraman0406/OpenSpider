import json
with open('./whatsapp_config.json', 'r') as f:
    d = json.load(f)
print(json.dumps(d, indent=2))

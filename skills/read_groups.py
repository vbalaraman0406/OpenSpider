import json

with open('/Users/vbalaraman/OpenSpider/workspace/whatsapp_config.json', 'r') as f:
    data = json.load(f)

print('=== allowedGroups ===')
for g in data.get('allowedGroups', []):
    print(json.dumps(g))

print('\n=== allowedDMs ===')
for d in data.get('allowedDMs', []):
    print(json.dumps(d))

print('\n=== defaultJid ===')
print(data.get('defaultJid', 'NOT SET'))

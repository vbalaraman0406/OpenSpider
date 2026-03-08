import json, os

config = {
  "dmPolicy": "allowlist",
  "allowedDMs": ["14156249639", "919940496224"],
  "groupPolicy": "allowlist",
  "allowedGroups": [
    {"jid": "120363423460684848@g.us", "mode": "mention"},
    {"jid": "14156249639-1373117853@g.us", "mode": "mention"},
    {"jid": "14156249639-1405615057@g.us", "mode": "mention"},
    {"jid": "120363023776108773@g.us", "mode": "mention"},
    {"jid": "120363423852747118@g.us", "mode": "mention"}
  ],
  "botMode": "mention"
}

path = 'workspace/whatsapp_config.json'
with open(path, 'w') as f:
    json.dump(config, f, indent=2)

# Verify
with open(path, 'r') as f:
    written = json.load(f)

assert written == config, 'MISMATCH'
print('Written and verified. Contents:')
print(json.dumps(written, indent=2))

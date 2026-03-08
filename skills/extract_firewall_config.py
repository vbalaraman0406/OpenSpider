with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Show lines 460-540 focusing on how config is loaded in the firewall section
for i in range(459, min(540, len(lines))):
    line = lines[i]
    if any(kw in line for kw in ['config', 'Config', 'JSON.parse', 'readFile', 'require', 'import', 'whatsapp_config', 'allowedDMs', 'dmPolicy', 'firewall', 'FIREWALL']):
        print(f'{i+1}: {line}', end='')

print('\n\n=== Full lines 460-475 ===')
for i in range(459, min(475, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')

print('\n\n=== Full lines 520-540 ===')
for i in range(519, min(540, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')

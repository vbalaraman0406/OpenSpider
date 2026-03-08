with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Show lines 325-340 where config is loaded
for i in range(324, min(340, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')

# Also check if there's a fromMe check before the firewall
print('\n\n=== Lines 395-440 (fromMe check) ===')
for i in range(394, min(440, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')

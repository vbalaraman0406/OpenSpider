import os

# List tools directory
tools_dir = '/Users/vbalaraman/OpenSpider/src/tools'
print('=== Tools directory ===')
for f in sorted(os.listdir(tools_dir)):
    print(f'  {f}')

# Search for send_whatsapp in tools directory
for f in os.listdir(tools_dir):
    fp = os.path.join(tools_dir, f)
    if os.path.isfile(fp) and f.endswith('.ts'):
        with open(fp, 'r') as fh:
            content = fh.read()
        if 'send_whatsapp' in content.lower() or 'whatsapp' in content.lower():
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'send_whatsapp' in line.lower() or 'sendwhatsapp' in line.lower():
                    start = max(0, i-2)
                    end = min(len(lines), i+15)
                    print(f'\n=== {f} lines {start+1}-{end} ===')
                    for j in range(start, end):
                        print(f'{j+1}: {lines[j]}')

# Read getParticipatingGroups function (lines 259-275)
with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

print('\n=== getParticipatingGroups (lines 259-280) ===')
for i in range(258, min(280, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')

# Read the full sendWhatsAppMessage including error handling (lines 280-360)
print('\n=== sendWhatsAppMessage error handling (lines 320-370) ===')
for i in range(319, min(370, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')

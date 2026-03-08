import os

# Search node_modules for the actual bot runtime that reads whatsapp_config
matches = []
for root, dirs, files in os.walk('node_modules'):
    dirs[:] = [d for d in dirs if d not in ('.git',)]
    for f in files:
        if not f.endswith(('.js', '.ts', '.mjs')):
            continue
        fp = os.path.join(root, f)
        try:
            sz = os.path.getsize(fp)
            if sz > 1000000:
                continue
            with open(fp, 'r', errors='ignore') as fh:
                content = fh.read()
                if 'botMode' in content and ('allowedDMs' in content or 'dmPolicy' in content):
                    matches.append(fp)
                    # Print relevant lines
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if any(kw in line for kw in ['botMode', 'allowedDMs', 'dmPolicy', 'isGroup', 'mention']):
                            print(f'{fp}:{i}: {line.strip()[:150]}')
                    print('---')
        except:
            pass

print(f'\nTotal files with botMode+allowedDMs: {len(matches)}')
for m in matches:
    print(f'  {m}')

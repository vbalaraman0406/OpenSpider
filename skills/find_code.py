import os
import re

# Find all .ts and .js files
code_files = []
for root, dirs, files in os.walk('.'):
    # Skip node_modules and .git
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '.next')]
    for f in files:
        if f.endswith(('.ts', '.js', '.mjs', '.cjs')):
            code_files.append(os.path.join(root, f))

print(f'Found {len(code_files)} code files')
for cf in code_files[:50]:
    print(cf)

print('\n--- Searching for allowedDMs/dmPolicy/allowlist references ---')
for cf in code_files:
    try:
        with open(cf, 'r', errors='ignore') as fh:
            content = fh.read()
            if any(kw in content for kw in ['allowedDMs', 'dmPolicy', 'allowlist', 'whatsapp_config']):
                # Find matching lines
                for i, line in enumerate(content.split('\n'), 1):
                    if any(kw in line for kw in ['allowedDMs', 'dmPolicy', 'allowlist', 'whatsapp_config']):
                        print(f'{cf}:{i}: {line.strip()}')
    except:
        pass

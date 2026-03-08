import os
import json

# Check package.json for entry point
try:
    with open('package.json', 'r') as f:
        pkg = json.load(f)
    print('=== package.json ===')
    print(f"name: {pkg.get('name')}")
    print(f"main: {pkg.get('main')}")
    print(f"scripts: {pkg.get('scripts', {})}")
    print(f"dependencies keys: {list(pkg.get('dependencies', {}).keys())[:20]}")
except Exception as e:
    print(f'No package.json: {e}')

# Find ALL files that contain 'allowedDMs' or 'dmPolicy' anywhere in the project
print('\n=== Deep search for allowedDMs/dmPolicy in ALL files ===')
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git', '.next')]
    # Include node_modules but only top-level packages
    for f in files:
        fp = os.path.join(root, f)
        if fp.endswith(('.ts', '.js', '.mjs', '.cjs', '.json')):
            # Skip huge files
            try:
                sz = os.path.getsize(fp)
                if sz > 500000:
                    continue
                with open(fp, 'r', errors='ignore') as fh:
                    content = fh.read()
                    if 'allowedDMs' in content or 'dmPolicy' in content:
                        if 'node_modules' not in fp or 'openspider' in fp.lower():
                            for i, line in enumerate(content.split('\n'), 1):
                                if 'allowedDMs' in line or 'dmPolicy' in line:
                                    print(f'{fp}:{i}: {line.strip()[:120]}')
            except:
                pass

# Check dist/ or build/ directories
print('\n=== Checking for dist/build dirs ===')
for d in ['dist', 'build', 'out', 'lib', '.output']:
    if os.path.isdir(d):
        print(f'{d}/ exists')
        for root2, dirs2, files2 in os.walk(d):
            for f2 in files2[:10]:
                print(f'  {os.path.join(root2, f2)}')

# Check if there's a monorepo or workspace structure
print('\n=== Top-level dirs ===')
for item in sorted(os.listdir('.')):
    if os.path.isdir(item) and not item.startswith('.'):
        print(f'  {item}/')

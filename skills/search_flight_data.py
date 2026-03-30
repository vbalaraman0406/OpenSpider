import os
import glob

memory_dir = '/Users/vbalaraman/OpenSpider/workspace/memory/'
skills_dir = '/Users/vbalaraman/OpenSpider/workspace/skills/'
workspace_dir = '/Users/vbalaraman/OpenSpider/workspace/'

keywords = ['alaska', 'flight', 'lax', 'pdx', 'sea to', 'fare', 'airfare', 'airline', 'round-trip', 'business class', 'premium']

results = []

# Search memory directory
if os.path.exists(memory_dir):
    for fname in sorted(os.listdir(memory_dir)):
        fpath = os.path.join(memory_dir, fname)
        if os.path.isfile(fpath):
            try:
                with open(fpath, 'r') as f:
                    content = f.read()
                content_lower = content.lower()
                matched = [k for k in keywords if k in content_lower]
                if matched:
                    results.append(f'\n=== MEMORY FILE: {fname} (matched: {", ".join(matched)}) ===\n{content[:2000]}')
            except:
                pass

# Search skills directory
if os.path.exists(skills_dir):
    for root, dirs, files in os.walk(skills_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r') as f:
                    content = f.read()
                content_lower = content.lower()
                matched = [k for k in keywords if k in content_lower]
                if matched:
                    results.append(f'\n=== SKILLS FILE: {os.path.relpath(fpath, skills_dir)} (matched: {", ".join(matched)}) ===\n{content[:2000]}')
            except:
                pass

# Also check workspace root for any relevant files
for fname in os.listdir(workspace_dir):
    fpath = os.path.join(workspace_dir, fname)
    if os.path.isfile(fpath):
        try:
            with open(fpath, 'r') as f:
                content = f.read()
            content_lower = content.lower()
            matched = [k for k in keywords if k in content_lower]
            if matched:
                results.append(f'\n=== WORKSPACE FILE: {fname} (matched: {", ".join(matched)}) ===\n{content[:2000]}')
        except:
            pass

if results:
    print('FOUND HISTORICAL FLIGHT DATA:')
    for r in results:
        print(r)
else:
    print('NO HISTORICAL FLIGHT PRICE DATA FOUND in memory/, skills/, or workspace root.')
    print('\nFiles checked in memory/:')
    if os.path.exists(memory_dir):
        for f in sorted(os.listdir(memory_dir)):
            print(f'  {f}')
    print('\nDirectories in skills/:')
    if os.path.exists(skills_dir):
        for f in sorted(os.listdir(skills_dir)):
            print(f'  {f}')
    else:
        print('  skills/ directory does not exist')

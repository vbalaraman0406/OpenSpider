import os, json, glob

# Check for any files mentioning karma in workspace
print('=== Searching workspace for karma references ===')
for root, dirs, files in os.walk('workspace'):
    for f in files:
        path = os.path.join(root, f)
        try:
            with open(path, 'r', errors='ignore') as fh:
                content = fh.read()
            if 'karma' in content.lower():
                lines = content.split('\n')
                karma_lines = [l.strip() for l in lines if 'karma' in l.lower()]
                print(f'\nFile: {path}')
                for l in karma_lines[:10]:
                    print(f'  {l[:200]}')
        except:
            pass

# Check memory directory
print('\n=== Memory directory contents ===')
mem_dir = 'workspace/memory'
if os.path.exists(mem_dir):
    files = sorted(os.listdir(mem_dir))
    print(f'Files: {files[-10:] if len(files) > 10 else files}')
else:
    print('No memory directory found')

# Check skills directory for karma scripts
print('\n=== Skills with karma references ===')
if os.path.exists('skills'):
    for f in os.listdir('skills'):
        if 'karma' in f.lower():
            print(f'  Skill file: {f}')

# Full cron_jobs.json dump
print('\n=== Full cron_jobs.json ===')
with open('workspace/cron_jobs.json', 'r') as f:
    print(f.read())

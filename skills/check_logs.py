import os, glob

config_path = '/Users/vbalaraman/OpenSpider/workspace/whatsapp_config.json'
print('=== whatsapp_config.json ===')
with open(config_path) as f:
    print(f.read())

print('\n=== Searching logs for 919940496224 ===')
log_dir = '/Users/vbalaraman/OpenSpider/logs'
if os.path.isdir(log_dir):
    for fpath in sorted(glob.glob(os.path.join(log_dir, '**', '*'), recursive=True)):
        if os.path.isfile(fpath):
            try:
                with open(fpath, 'r', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if '919940496224' in line:
                            print(f'[{fpath}:{i+1}] {line.rstrip()[:300]}')
            except Exception as e:
                print(f'Error reading {fpath}: {e}')
else:
    print('No logs/ directory found')

print('\n=== Recent error lines in logs ===')
if os.path.isdir(log_dir):
    for fpath in sorted(glob.glob(os.path.join(log_dir, '**', '*'), recursive=True)):
        if os.path.isfile(fpath):
            try:
                with open(fpath, 'r', errors='ignore') as f:
                    lines = f.readlines()
                    err_lines = [(i+1, l.rstrip()) for i, l in enumerate(lines) if 'error' in l.lower() or 'Error' in l]
                    for ln, txt in err_lines[-10:]:
                        print(f'[{fpath}:{ln}] {txt[:300]}')
            except Exception as e:
                pass

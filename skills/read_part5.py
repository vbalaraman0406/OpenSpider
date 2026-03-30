import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Read test_regression.py lines 30-80 (the middle part that was truncated)
path = os.path.join(base, 'backend/test_regression.py')
with open(path) as fh:
    lines = fh.readlines()
    for i, line in enumerate(lines):
        print(f'{i+1:3d}: {line}', end='')

print('\n\n--- requirements.txt ---')
req_path = os.path.join(base, 'backend/requirements.txt')
if os.path.exists(req_path):
    with open(req_path) as fh:
        print(fh.read())
else:
    print('NOT FOUND')

# Also check if there's a top-level requirements.txt
req_path2 = os.path.join(base, 'requirements.txt')
if os.path.exists(req_path2):
    print('\n--- top-level requirements.txt ---')
    with open(req_path2) as fh:
        print(fh.read())

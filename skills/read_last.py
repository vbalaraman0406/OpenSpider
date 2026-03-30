import os
path = 'skills/downdetector_last.md'
if os.path.exists(path):
    with open(path, 'r') as f:
        print(f.read())
else:
    print('FILE_NOT_FOUND')
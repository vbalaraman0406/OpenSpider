import os
import json

path = 'workspace/bmo_downdetector_last.json'
if os.path.exists(path):
    with open(path, 'r') as f:
        print(f.read())
else:
    print('NO_PREVIOUS_DATA')

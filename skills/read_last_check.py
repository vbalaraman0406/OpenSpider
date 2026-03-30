import os

path = 'workspace/memory/trump_truth_last_check.md'
if os.path.exists(path):
    with open(path, 'r') as f:
        print(f.read())
else:
    print('FILE_NOT_FOUND')

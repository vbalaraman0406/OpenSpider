import os

file_path = 'workspace/trump_last_seen.txt'
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    print('FILE_EXISTS')
    print(repr(content))
else:
    print('FILE_NOT_FOUND')

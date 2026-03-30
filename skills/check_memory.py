import os

memory_path = 'workspace/memory/trump_truth_social_last_check.md'

if os.path.exists(memory_path):
    with open(memory_path, 'r') as f:
        content = f.read()
    print('FILE_EXISTS')
    print(content)
else:
    print('FILE_NOT_FOUND')

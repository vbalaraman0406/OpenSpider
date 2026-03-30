import os

path = './workspace/skills/trump_truth_last_check'
if os.path.isdir(path):
    print('Is a directory. Contents:')
    for f in os.listdir(path):
        full = os.path.join(path, f)
        print(f'  {f} (file={os.path.isfile(full)})')
        if os.path.isfile(full):
            with open(full, 'r') as fh:
                print(f'  Content: {fh.read()}')
elif os.path.isfile(path):
    with open(path, 'r') as f:
        print(f'File content: {f.read()}')
else:
    print('Path does not exist')

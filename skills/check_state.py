import os, json

state_path = 'workspace/skills/trump_truth_last_check/state.json'
os.makedirs(os.path.dirname(state_path), exist_ok=True)

try:
    with open(state_path, 'r') as f:
        state = json.load(f)
    print(json.dumps(state))
except FileNotFoundError:
    print('FILE_NOT_FOUND')

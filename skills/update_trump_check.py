import json
import datetime

state_path = 'workspace/skills/trump_truth_last_check/state.json'

# Read current state
with open(state_path, 'r') as f:
    state = json.load(f)

# Update with current timestamp
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7)))
state['last_check'] = now.isoformat()

# Write back
with open(state_path, 'w') as f:
    json.dump(state, f, indent=2)

print(f'Updated last_check to: {now.isoformat()}')
print(f'State: {json.dumps(state, indent=2)}')

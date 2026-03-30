import os, json

workspace = os.path.join(os.getcwd(), 'workspace')
draft_file = os.path.join(workspace, 'linkedin_draft.json')

if os.path.exists(draft_file):
    with open(draft_file, 'r') as f:
        draft = json.load(f)
    print(f"Status: {draft.get('status')}")
    print(f"Chars: {draft.get('char_count')}")
    print(f"Text preview: {draft.get('text', '')[:300]}")
else:
    print('No draft file found')
    # List workspace contents
    if os.path.exists(workspace):
        print(f'Workspace contents: {os.listdir(workspace)}')
    else:
        print('Workspace dir does not exist')
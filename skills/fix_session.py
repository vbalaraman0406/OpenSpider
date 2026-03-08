import os

session_file = '/Users/vbalaraman/OpenSpider/baileys_auth_info/session-919940496224.0.json'

if os.path.exists(session_file):
    os.remove(session_file)
    print(f'DELETED: {session_file}')
else:
    print(f'File not found: {session_file}')

# Verify deletion
if not os.path.exists(session_file):
    print('Session file successfully removed.')
else:
    print('ERROR: File still exists!')

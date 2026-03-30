with open('workspace/memory.md', 'r') as f:
    content = f.read()

append_block = '''

## User Preferences

- **BMO Downdetector Monitoring Rule (CRITICAL)**: NEVER send a WhatsApp message when BMO Downdetector shows NO issues. Only send a message if there IS an active outage or problem detected. This is a hard rule — the user has requested this multiple times. Silence = no issues. Do NOT confirm 'all clear' or 'no issues found' — just stay silent.
'''

if '## User Preferences' in content:
    # Find the section and append the rule if not already there
    if 'BMO Downdetector Monitoring Rule' not in content:
        # Insert after the User Preferences header
        idx = content.index('## User Preferences')
        end_of_line = content.index('\n', idx)
        content = content[:end_of_line] + '\n\n- **BMO Downdetector Monitoring Rule (CRITICAL)**: NEVER send a WhatsApp message when BMO Downdetector shows NO issues. Only send a message if there IS an active outage or problem detected. This is a hard rule — the user has requested this multiple times. Silence = no issues. Do NOT confirm \'all clear\' or \'no issues found\' — just stay silent.' + content[end_of_line:]
        with open('workspace/memory.md', 'w') as f:
            f.write(content)
        print('Rule appended to existing User Preferences section.')
    else:
        print('Rule already exists in memory.md')
else:
    content += append_block
    with open('workspace/memory.md', 'w') as f:
        f.write(content)
    print('User Preferences section created with BMO rule.')

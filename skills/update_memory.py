import os

BASE = '/Users/vbalaraman/OpenSpider'
paths = [os.path.join(BASE, 'memory.md'), os.path.join(BASE, 'skills', 'memory.md')]

for p in paths:
    with open(p, 'r') as f:
        content = f.read()
    
    # 1. Add CEO under Identity section
    # Find the Identity section and add CEO after the existing entries
    identity_marker = '## Identity'
    if '**CEO**' not in content:
        # Insert after the last line of the Identity section (before next ## or blank line pattern)
        lines = content.split('\n')
        new_lines = []
        in_identity = False
        ceo_added = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == '## Identity':
                in_identity = True
                continue
            if in_identity and not ceo_added:
                # Check if next line is empty or a new section
                if line.strip() == '' or (i+1 < len(lines) and lines[i+1].strip().startswith('## ')):
                    # Insert CEO before this blank line
                    new_lines.insert(-1, '- **CEO**: Vishnu Balaraman')
                    ceo_added = True
                    in_identity = False
                elif line.strip().startswith('- **Vibe**'):
                    new_lines.append('- **CEO**: Vishnu Balaraman')
                    ceo_added = True
                    in_identity = False
        content = '\n'.join(new_lines)
    
    # 2. Update User Profile section
    lines = content.split('\n')
    new_lines = []
    in_user_profile = False
    name_updated = False
    role_updated = False
    for i, line in enumerate(lines):
        if line.strip() == '## User Profile':
            in_user_profile = True
            new_lines.append(line)
            continue
        if in_user_profile and line.strip().startswith('## '):
            # Exiting user profile section - add missing entries before leaving
            if not name_updated:
                new_lines.append('- **Name**: Vishnu Balaraman')
            if not role_updated:
                new_lines.append('- **Role**: CEO of Ananta Ventures LLC')
            in_user_profile = False
            new_lines.append(line)
            continue
        if in_user_profile:
            if line.strip().startswith('- **Primary User**'):
                new_lines.append('- **Name**: Vishnu Balaraman')
                new_lines.append('- **Role**: CEO of Ananta Ventures LLC')
                new_lines.append(line)
                name_updated = True
                role_updated = True
                continue
            if line.strip().startswith('- **Name**'):
                new_lines.append('- **Name**: Vishnu Balaraman')
                name_updated = True
                continue
            if line.strip().startswith('- **Role**'):
                new_lines.append('- **Role**: CEO of Ananta Ventures LLC')
                role_updated = True
                continue
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    with open(p, 'w') as f:
        f.write(content)
    print(f'Updated: {p}')

# Print final contents
for p in paths:
    print(f'\n===== {p} =====')
    with open(p, 'r') as f:
        print(f.read())

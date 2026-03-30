import os
import subprocess

# Search for the actual backend server code
print('=== Looking for server/agent code ===')
for root, dirs, files in os.walk('.'):
    # Skip node_modules and .git
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '.next', 'build', 'dist']]
    for f in files:
        if f in ['server.js', 'server.ts', 'index.js', 'index.ts', 'app.js', 'app.ts', 'main.js', 'main.ts']:
            filepath = os.path.join(root, f)
            print(f'Found: {filepath}')

print('\n=== Looking for .env files ===')
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git']]
    for f in files:
        if f.startswith('.env'):
            filepath = os.path.join(root, f)
            print(f'Found: {filepath}')
            # Read and show relevant lines (mask secrets)
            try:
                with open(filepath, 'r') as fh:
                    for line in fh:
                        line = line.strip()
                        lower = line.lower()
                        if any(kw in lower for kw in ['model', 'openai', 'anthropic', 'claude', 'token', 'llm', 'api']):
                            # Mask the value
                            if '=' in line:
                                key = line.split('=')[0]
                                print(f'  {key}=***')
                            else:
                                print(f'  {line}')
            except:
                pass

print('\n=== Checking workspace for logs ===')
for root, dirs, files in os.walk('./workspace'):
    for f in files:
        filepath = os.path.join(root, f)
        size = os.path.getsize(filepath)
        print(f'{filepath} ({size} bytes)')

print('\n=== Checking skills directory ===')
for root, dirs, files in os.walk('./skills'):
    for f in files:
        filepath = os.path.join(root, f)
        print(filepath)

# Check if there's a parent directory with the backend
print('\n=== Parent directory contents ===')
try:
    parent = os.path.dirname(os.getcwd())
    for item in sorted(os.listdir(parent)):
        full = os.path.join(parent, item)
        if os.path.isdir(full):
            print(f'DIR:  {item}')
        else:
            print(f'FILE: {item}')
except:
    print('Cannot access parent directory')

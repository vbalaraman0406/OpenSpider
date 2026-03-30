import os
import subprocess

# Search for files containing LLM-related keywords
keywords = ['openai', 'anthropic', 'claude', 'token_usage', 'prompt_tokens', 'completion_tokens', 'total_tokens', 'usage']

# First, let's see what's in the workspace directory
for root, dirs, files in os.walk('.'):
    # Skip node_modules
    if 'node_modules' in root:
        continue
    for f in files:
        if f.endswith(('.js', '.ts', '.mjs', '.cjs', '.py', '.json', '.log', '.txt')):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', errors='ignore') as fh:
                    content = fh.read()
                    for kw in keywords:
                        if kw.lower() in content.lower():
                            print(f'MATCH [{kw}]: {filepath}')
                            break
            except:
                pass

# Also check workspace for any log files or token tracking
print('\n--- Workspace files ---')
for root, dirs, files in os.walk('./workspace'):
    for f in files:
        print(os.path.join(root, f))

# Check skills directory
print('\n--- Skills files ---')
for root, dirs, files in os.walk('./skills'):
    for f in files:
        print(os.path.join(root, f))

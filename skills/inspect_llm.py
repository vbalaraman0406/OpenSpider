import os

files_to_check = [
    './create_files.py',
    './write_youtube_script.py', 
    './process_downdetector.py',
    './trending3.py',
    './health_check.py',
    './send_voice.py'
]

for f in files_to_check:
    if os.path.exists(f):
        print(f'\n===== {f} =====')
        with open(f, 'r', errors='ignore') as fh:
            content = fh.read()
            # Find lines with token/usage/openai/anthropic
            lines = content.split('\n')
            for i, line in enumerate(lines):
                lower = line.lower()
                if any(kw in lower for kw in ['openai', 'anthropic', 'claude', 'token', 'usage', 'model', 'completion', 'api_key']):
                    print(f'  L{i+1}: {line.strip()}')

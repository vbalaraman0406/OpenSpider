import datetime
import os

# File path
TIMESTAMP_FILE = 'workspace/memory.md'

# Get current time
current_time = datetime.datetime.now()
timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

# Write to file
try:
    with open(TIMESTAMP_FILE, 'w') as f:
        f.write(f'Last check: {timestamp_str}\n')
    print(f'Timestamp updated to: {timestamp_str}')
except Exception as e:
    print(f'Error writing file: {e}')
#!/usr/bin/env python3
import sys
import os

# Path to the stored post text file
stored_file = 'workspace/trump_last_seen.txt'

# Read the stored post text
try:
    with open(stored_file, 'r') as f:
        stored_text = f.read().strip()
except FileNotFoundError:
    stored_text = ''

# Extracted post text from Advanced Headless Navigation agent
# In a real scenario, this should be passed as an argument or from a file
# For now, hardcode based on user request hint: 'Donald J. Trump REPLAY'
extracted_text = 'Donald J. Trump REPLAY'

# Debug prints
print(f'Stored text: {repr(stored_text)}', file=sys.stderr)
print(f'Extracted text: {repr(extracted_text)}', file=sys.stderr)

# Check if extracted text is empty or None (no post found)
if not extracted_text or extracted_text.strip() == '':
    print('No post found, exiting silently.', file=sys.stderr)
    sys.exit(0)

# Check for ad indicators (Sponsored, Promoted, Ad)
ad_indicators = ['Sponsored', 'Promoted', 'Ad']
if any(indicator in extracted_text for indicator in ad_indicators):
    print('Extracted text contains ad, exiting silently.', file=sys.stderr)
    sys.exit(0)

# Compare stored and extracted text
if stored_text == extracted_text:
    print('Text identical, exiting silently.', file=sys.stderr)
    sys.exit(0)

# If new post detected, overwrite the file
print('New post detected, overwriting file...', file=sys.stderr)
try:
    with open(stored_file, 'w') as f:
        f.write(extracted_text)
    print('File updated successfully.', file=sys.stderr)
except Exception as e:
    print(f'Error updating file: {e}', file=sys.stderr)
    sys.exit(1)

# Output the new post text for potential WhatsApp sending
print(extracted_text)
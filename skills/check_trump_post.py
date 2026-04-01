#!/usr/bin/env python3
import os
import sys

# Paths
last_seen_file = 'workspace/trump_last_seen.txt'
new_text_file = 'workspace/new_post.txt'  # Assume new text is saved here from previous step

# Read new post text (from file for safety)
new_text = ''
if os.path.exists(new_text_file):
    with open(new_text_file, 'r') as f:
        new_text = f.read().strip()
else:
    # If no file, assume no new text (e.g., from stdin in real scenario)
    # For cron task, we might get it via environment or direct pass, but here exit
    print('NO_NEW_TEXT')
    sys.exit(0)

# Check if new text is empty or likely an ad
if not new_text or 'Sponsored' in new_text or 'Promoted' in new_text or 'Ad' in new_text:
    print('NO_CHANGE_OR_AD')
    sys.exit(0)

# Read old text
old_text = ''
if os.path.exists(last_seen_file):
    with open(last_seen_file, 'r') as f:
        old_text = f.read().strip()

# Compare
if new_text == old_text:
    print('NO_CHANGE')
    sys.exit(0)

# Overwrite with new text
with open(last_seen_file, 'w') as f:
    f.write(new_text)
print('NEW_TEXT:' + new_text)
# Note: WhatsApp sending will be handled separately based on this output
#!/usr/bin/env python3
import os
import sys

# Paths
new_text_file = 'workspace/new_post.txt'
last_seen_file = 'workspace/trump_last_seen.txt'

# Step 1: Read new post text
if not os.path.exists(new_text_file):
    # No new text file, exit silently as per instructions (no post found)
    sys.exit(0)

with open(new_text_file, 'r') as f:
    new_text = f.read().strip()

# Step 2: Check if new text is empty or likely an ad
if not new_text or 'Sponsored' in new_text or 'Promoted' in new_text or 'Ad' in new_text:
    # Exit silently without sending messages
    sys.exit(0)

# Step 3: Read old text
old_text = ''
if os.path.exists(last_seen_file):
    with open(last_seen_file, 'r') as f:
        old_text = f.read().strip()

# Step 4: Compare
if new_text == old_text:
    # Identical, exit silently
    sys.exit(0)

# Step 5: Overwrite with new text
with open(last_seen_file, 'w') as f:
    f.write(new_text)

# Step 6: Output new text for WhatsApp sending
print(new_text)
sys.exit(0)
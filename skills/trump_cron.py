#!/usr/bin/env python3
import os
import sys
import json

# Paths
last_seen_file = 'workspace/trump_last_seen.txt'
new_text_file = 'workspace/new_post.txt'  # Expected to contain extracted post text from Advanced Headless Navigation agent

# Step 1: Read new post text
new_text = ''
if os.path.exists(new_text_file):
    with open(new_text_file, 'r') as f:
        new_text = f.read().strip()
else:
    # No new text file, exit silently as per instructions (no post found)
    sys.exit(0)

# Step 2: Check if new text is empty or an ad
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

# Step 6: Send WhatsApp messages
recipients = [
    '14156249639@s.whatsapp.net',
    '16507965072@s.whatsapp.net',
    '120363423852747118@g.us'
]
# In a real scenario, we'd call send_whatsapp tool here, but for script output, prepare data
result = {
    'new_text': new_text,
    'recipients': recipients,
    'status': 'READY_FOR_WHATSAPP'
}
print(json.dumps(result))
# Note: Actual WhatsApp sending will be handled by calling the send_whatsapp tool based on this output
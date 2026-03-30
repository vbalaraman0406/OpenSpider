import os

memory_dir = '/Users/vbalaraman/OpenSpider/workspace/memory'
os.makedirs(memory_dir, exist_ok=True)

checkpoint_content = """Last Check: 2026-03-21 03:48:00 PDT
Status: CHECK FAILED - Browser relay unavailable and HTTP requests blocked
Last Known Post: ~2:47 PM PDT 2026-03-20 - Iran war winding down
No WhatsApp alert sent (unable to verify new posts)"""

with open(os.path.join(memory_dir, 'trump_truth_last_check.md'), 'w') as f:
    f.write(checkpoint_content)

print('Checkpoint file updated successfully')

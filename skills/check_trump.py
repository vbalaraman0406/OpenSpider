import os
import datetime

last_check_path = 'workspace/memory/trump_truth_last_check.md'

# Read existing file if present
if os.path.exists(last_check_path):
    with open(last_check_path, 'r') as f:
        print('EXISTING FILE CONTENT:')
        print(f.read())
else:
    print('FILE_NOT_FOUND')

# The most recent post from the scan was March 21, 2026 at 7:44 PM PDT
# Current time is March 22, 2026 at 12:30 AM PDT
# 7:44 PM is ~4 hours 46 minutes ago — well outside the 30-minute window
# No new posts to alert on.

# Update the last check file silently
with open(last_check_path, 'w') as f:
    f.write('# Trump Truth Social - Last Check\n')
    f.write('\n')
    f.write('## Last Check Time\n')
    f.write('Sunday, March 22, 2026 at 12:30 AM PDT\n')
    f.write('\n')
    f.write('## Last Post Found\n')
    f.write('- **Timestamp:** Saturday, March 21, 2026 at 7:44 PM PDT\n')
    f.write('- **Status:** No new posts within 30-min window. No alert sent.\n')
    f.write('- **Content Fingerprint:** trump_truth_2026-03-21_1944_pdt\n')

print('\nLast check file updated successfully.')
print('RESULT: NO_NEW_POSTS')

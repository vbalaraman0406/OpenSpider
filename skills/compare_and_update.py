#!/usr/bin/env python3
import sys

# New post text extracted from Advanced Headless Navigation agent
new_post = "I have just met with various Political Representatives of the tragedy that took place in California concerning the burning of thousands of once beautiful homes. It was brought to my attention that the Insurance Companies, in particular, State Farm, have been absolutely horrible to people that have been paying them large Premiums for years, only to find that ... [COMPACTED 440 chars] ... d in which we live, nothing really surprises me! State Farm, and others, should get their act together, and treat people fairly. The Government is looking into this matter as we speak! President DONALD J. TRUMP"

# Read the saved text from file
try:
    with open('workspace/trump_last_seen.txt', 'r') as f:
        saved_text = f.read().strip()
except FileNotFoundError:
    saved_text = ""

# Compare texts
if saved_text == new_post:
    print("Texts are identical. Exiting silently.")
    sys.exit(0)
else:
    # Overwrite file with new text
    with open('workspace/trump_last_seen.txt', 'w') as f:
        f.write(new_post)
    print("File updated with new post text.")
    sys.exit(1)  # Exit with code 1 to indicate new text and proceed to WhatsApp send
import os

content = """Last check: 2026-03-21 01:52:39


## User Preferences

- **BMO Downdetector Monitoring Rule (CRITICAL)**: NEVER send a WhatsApp message when BMO Downdetector shows NO issues. Only send a message if there IS an active outage or problem detected. This is a hard rule — the user has requested this multiple times. Silence = no issues. Do NOT confirm 'all clear' or 'no issues found' — just stay silent.
- **BMO Monitoring: NEVER send messages when no issues are reported. Only alert when there is an active outage or problem. This is a critical, repeated user directive. The CEO has ordered this MULTIPLE times. Any violation is forbidden.**
"""

with open('workspace/memory.md', 'w') as f:
    f.write(content)

print('memory.md updated successfully')
print(open('workspace/memory.md').read())

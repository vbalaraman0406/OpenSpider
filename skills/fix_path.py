import os

dir_path = 'workspace/memory'
os.makedirs(dir_path, exist_ok=True)

content = """# Trump Truth Social - Last Check
- **Last Check Time:** 2026-03-21 13:02 PDT
- **Last Post Timestamp:** ~12:12-12:25 PM PDT, March 21, 2026
- **Last Post Preview:** "Robert Mueller just died. Good, I'm glad he's dead. He put me through hell, and he was a dirty cop..."
- **Alert Sent:** Yes
- **Source:** Google News aggregation (NYT, Reuters, Fox News, Rolling Stone, Politico, CNBC)
"""

with open(os.path.join(dir_path, 'trump_truth_last_check.md'), 'w') as f:
    f.write(content)

print('File written successfully to workspace/memory/trump_truth_last_check.md')

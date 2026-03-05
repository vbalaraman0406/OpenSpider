with open('wa_summary.txt', 'r') as f:
    wa = f.read()
with open('md_table.txt', 'r') as f:
    md = f.read()
print('===WA_SUMMARY===')
print(wa[:1500])
print('===MD_TABLE===')
print(md[:2000])

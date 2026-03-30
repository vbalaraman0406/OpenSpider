# Read the current whatsapp.ts file
with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    content = f.read()

# The fix: modify the error handling in sendWhatsAppMessage to also catch 'not-acceptable' errors
# Current code at line 288:
#   if (e?.message?.includes('No sessions') || e?.name === 'SessionError') {
# Replace with:
#   if (e?.message?.includes('No sessions') || e?.name === 'SessionError' || e?.message?.includes('not-acceptable') || e?.output?.statusCode === 406) {

old_condition = "if (e?.message?.includes('No sessions') || e?.name === 'SessionError') {"
new_condition = "if (e?.message?.includes('No sessions') || e?.name === 'SessionError' || e?.message?.includes('not-acceptable') || e?.output?.statusCode === 406) {"

old_warn = '''console.warn(`[WhatsApp] "No sessions" error for ${jid}. Force-refreshing sessions...`);'''
new_warn = '''console.warn(`[WhatsApp] Session/delivery error for ${jid}: ${e?.message?.substring(0, 100)}. Force-refreshing sessions...`);'''

if old_condition in content:
    content = content.replace(old_condition, new_condition)
    content = content.replace(old_warn, new_warn)
    
    with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'w') as f:
        f.write(content)
    print('SUCCESS: Updated sendWhatsAppMessage to handle not-acceptable errors')
    print(f'Old condition: {old_condition}')
    print(f'New condition: {new_condition}')
else:
    print('ERROR: Could not find the target string to replace')
    # Show what's around line 288
    lines = content.split('\n')
    for i in range(286, 292):
        print(f'{i+1}: {lines[i]}')

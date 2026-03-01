import re

# Read the file
with open('/Users/vbalaraman/OpenSpider/src/agents/WorkerAgent.ts', 'r') as f:
    content = f.read()

# The broken pattern: the send_email block is AFTER the else block
# We need to find the else block and the send_email block, then swap their order

# Strategy: find the pattern where else { ... } is followed by send_email else-if
# and restructure so send_email comes BEFORE the else

old_pattern = """} else {
                    toolOutput = `Unknown action: ${response.action}`;
                }
            } else if (response.action === 'send_email') {"""

new_pattern = """} else if (response.action === 'send_email') {"""

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print('Fixed: moved send_email before else block')
else:
    print('Pattern not found, trying alternate approach')
    print(repr(content[content.find('Unknown action'):content.find('Unknown action')+200]))

# Now we need to add the else block back AFTER the send_email block's closing brace
# Find the send_email block end and add else before } catch
old_end = """                    toolOutput = emailResult.success ? `Email sent successfully. Message ID: ${emailResult.messageId}` : `Email send failed: ${emailResult.error}`;
            } catch"""

new_end = """                    toolOutput = emailResult.success ? `Email sent successfully. Message ID: ${emailResult.messageId}` : `Email send failed: ${emailResult.error}`;
                } else {
                    toolOutput = `Unknown action: ${response.action}`;
                }
            } catch"""

if old_end in content:
    content = content.replace(old_end, new_end)
    print('Fixed: added else block after send_email')
else:
    print('End pattern not found')

with open('/Users/vbalaraman/OpenSpider/src/agents/WorkerAgent.ts', 'w') as f:
    f.write(content)

print('Done')

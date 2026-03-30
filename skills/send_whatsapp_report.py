#!/usr/bin/env python3
import os
import sys

# Define the report file path
report_path = 'workspace/vancouver_homes_report.md'
# Define the WhatsApp target
target_jid = '14156249639@s.whatsapp.net'
# Define the brief message
brief_message = 'Here are the latest 5-bedroom, 2.5-3 bathroom homes in Vancouver WA area under $800K, built 2017 or newer.'

# Check if the report file exists
if not os.path.exists(report_path):
    print(f"Error: Report file '{report_path}' not found.", file=sys.stderr)
    sys.exit(1)

# Read the report content
with open(report_path, 'r') as file:
    report_content = file.read()

# Check if report content is empty
if not report_content.strip():
    print("Warning: Report file is empty. No listings found.", file=sys.stderr)
    # Still proceed to send the message with empty report

# Format the full message to send
full_message = f"{brief_message}\n\n--- Report ---\n{report_content}"

# Output the details for sending (simulating send_whatsapp tool)
print(f"WhatsApp Target: {target_jid}")
print(f"Message to send:")
print(full_message)
print("\nNote: This script simulates sending via WhatsApp. In a real setup, integrate with a WhatsApp API or tool.")

# Optionally, save the formatted message to a file for manual sending
output_path = 'workspace/whatsapp_message.txt'
with open(output_path, 'w') as out_file:
    out_file.write(full_message)
print(f"Formatted message saved to {output_path} for manual sending.")
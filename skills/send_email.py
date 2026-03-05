#!/usr/bin/env python3
import os
import re
import base64
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

# ──────────────────────────────────────────────────
# Markdown → HTML converter (no external dependencies)
# ──────────────────────────────────────────────────

def md_to_html(md_text: str) -> str:
    """Convert markdown text to clean HTML. Handles headers, bold, italic,
    links, code blocks, horizontal rules, tables, and lists."""
    lines = md_text.split('\n')
    html_lines = []
    in_table = False
    in_code_block = False
    in_list = False
    table_rows = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            return ''
        out = '<table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;">\n'
        for idx, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip('|').split('|')]
            tag = 'th' if idx == 0 else 'td'
            style_header = 'background:#1a1a2e;color:#e0e0ff;padding:10px 14px;text-align:left;border-bottom:2px solid #333;font-weight:600;'
            style_cell = 'padding:10px 14px;border-bottom:1px solid #2a2a3a;color:#c8c8d8;'
            row_bg = '' if idx % 2 == 0 else ' style="background:#12121f;"'
            out += f'<tr{row_bg}>'
            for cell in cells:
                st = style_header if idx == 0 else style_cell
                out += f'<{tag} style="{st}">{inline_format(cell)}</{tag}>'
            out += '</tr>\n'
        out += '</table>\n'
        table_rows = []
        in_table = False
        return out

    def inline_format(text: str) -> str:
        """Apply inline markdown formatting: bold, italic, links, code, emoji."""
        # Links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#6c9fff;text-decoration:none;">\1</a>', text)
        # Bold+italic: ***text*** or ___text___
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        # Bold: **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#fff;">\1</strong>', text)
        # Italic: *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # Inline code: `text`
        text = re.sub(r'`(.+?)`', r'<code style="background:#1a1a2e;padding:2px 6px;border-radius:4px;font-size:13px;color:#a5b4fc;">\1</code>', text)
        return text

    for line in lines:
        stripped = line.strip()

        # Code blocks
        if stripped.startswith('```'):
            if in_code_block:
                html_lines.append('</pre>')
                in_code_block = False
            else:
                html_lines.append('<pre style="background:#0d0d1a;border:1px solid #2a2a3a;border-radius:8px;padding:16px;overflow-x:auto;font-size:13px;color:#a5b4fc;margin:12px 0;">')
                in_code_block = True
            continue
        if in_code_block:
            html_lines.append(line)
            continue

        # Tables
        if '|' in stripped and stripped.startswith('|'):
            # Skip separator rows (|---|---|)
            if re.match(r'^\|[\s\-:|]+\|$', stripped):
                continue
            if not in_table:
                in_table = True
            table_rows.append(stripped)
            continue
        elif in_table:
            html_lines.append(flush_table())

        # Horizontal rule
        if re.match(r'^-{3,}$|^\*{3,}$|^_{3,}$', stripped):
            html_lines.append('<hr style="border:none;border-top:1px solid #2a2a3a;margin:20px 0;">')
            continue

        # Headers
        if stripped.startswith('######'):
            html_lines.append(f'<h6 style="color:#a5b4fc;font-size:13px;margin:12px 0 4px;font-weight:600;">{inline_format(stripped[6:].strip())}</h6>')
        elif stripped.startswith('#####'):
            html_lines.append(f'<h5 style="color:#a5b4fc;font-size:14px;margin:12px 0 4px;font-weight:600;">{inline_format(stripped[5:].strip())}</h5>')
        elif stripped.startswith('####'):
            html_lines.append(f'<h4 style="color:#c7d2fe;font-size:15px;margin:14px 0 6px;font-weight:600;">{inline_format(stripped[4:].strip())}</h4>')
        elif stripped.startswith('###'):
            html_lines.append(f'<h3 style="color:#c7d2fe;font-size:16px;margin:16px 0 8px;font-weight:600;">{inline_format(stripped[3:].strip())}</h3>')
        elif stripped.startswith('##'):
            html_lines.append(f'<h2 style="color:#e0e0ff;font-size:18px;margin:20px 0 10px;font-weight:700;border-bottom:1px solid #2a2a3a;padding-bottom:6px;">{inline_format(stripped[2:].strip())}</h2>')
        elif stripped.startswith('#'):
            html_lines.append(f'<h1 style="color:#fff;font-size:22px;margin:24px 0 12px;font-weight:700;">{inline_format(stripped[1:].strip())}</h1>')
        # Unordered list
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul style="margin:8px 0;padding-left:24px;color:#c8c8d8;">')
                in_list = True
            html_lines.append(f'<li style="margin:4px 0;line-height:1.6;">{inline_format(stripped[2:])}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            # Regular paragraph
            if stripped:
                html_lines.append(f'<p style="color:#c8c8d8;line-height:1.7;margin:8px 0;font-size:14px;">{inline_format(stripped)}</p>')
            else:
                html_lines.append('')

    # Flush remaining table
    if in_table:
        html_lines.append(flush_table())
    if in_list:
        html_lines.append('</ul>')

    return '\n'.join(html_lines)


def get_agent_name() -> str:
    """Read the Manager agent's persona name from IDENTITY.md."""
    try:
        identity_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace', 'agents', 'manager', 'IDENTITY.md')
        if os.path.exists(identity_path):
            with open(identity_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('Name:'):
                        return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return 'OpenSpider'


def wrap_in_email_template(html_body: str, subject: str = '') -> str:
    """Wrap HTML content in a professional dark-themed email template."""
    agent_name = get_agent_name()
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#0a0a14;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0a0a14;">
<tr><td align="center" style="padding:20px 0;">
<table role="presentation" width="640" cellspacing="0" cellpadding="0" style="background:#111127;border-radius:12px;border:1px solid #1e1e3a;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.4);">

<!-- Header -->
<tr>
<td style="background:linear-gradient(135deg,#1e1b4b,#312e81);padding:24px 32px;">
<table width="100%" cellspacing="0" cellpadding="0">
<tr>
<td>
  <span style="font-size:24px;font-weight:700;color:#fff;letter-spacing:-0.5px;">♾️ {agent_name}</span>
  <br/>
  <span style="font-size:12px;color:#a5b4fc;letter-spacing:1px;text-transform:uppercase;">Autonomous Agent Report</span>
</td>
<td align="right" style="vertical-align:top;">
  <span style="font-size:11px;color:#818cf8;background:#1e1b4b;padding:4px 10px;border-radius:20px;border:1px solid #312e81;">Automated</span>
</td>
</tr>
</table>
</td>
</tr>

<!-- Body -->
<tr>
<td style="padding:28px 32px;">
{html_body}
</td>
</tr>

<!-- Footer -->
<tr>
<td style="background:#0d0d1a;padding:16px 32px;border-top:1px solid #1e1e3a;">
<table width="100%" cellspacing="0" cellpadding="0">
<tr>
<td style="font-size:11px;color:#64648a;line-height:1.5;">
  Powered by ♾️ <strong style="color:#818cf8;">{agent_name}</strong> — OpenSpider Agent System<br/>
  This is an automated message. Do not reply directly.
</td>
<td align="right" style="font-size:11px;color:#64648a;">
  🔒 Secure • 🤖 AI-Generated
</td>
</tr>
</table>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>'''


def load_credentials():
    workspace_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')
    creds_path = os.path.join(workspace_dir, 'gmail_credentials.json')
    token_path = os.path.join(workspace_dir, 'gmail_token.json')

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                # Scopes likely changed or token revoked. Delete stale token and force re-auth.
                print("Token refresh failed (likely due to expanded scopes). Forcing re-authentication...")
                if os.path.exists(token_path):
                    os.remove(token_path)
                creds = None

        if not creds:
            if not os.path.exists(creds_path):
                print(f"Error: Missing {creds_path}.")
                print("Please run `openspider tools email setup` to configure OAuth credentials.")
                return None
            
            # Since scopes changed, we must force a new browser login if the token got invalid/refused
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

def send_email(to_email, subject, body):
    creds = load_credentials()
    if not creds:
        return False

    try:
        service = build('gmail', 'v1', credentials=creds)

        # Convert markdown body to styled HTML with professional template
        html_body = md_to_html(body)
        styled_html = wrap_in_email_template(html_body, subject)

        message = MIMEMultipart()
        message['To'] = to_email
        message['Subject'] = subject
        msg = MIMEText(styled_html, 'html')
        message.attach(msg)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body_payload = {'raw': raw_message}

        send_message = service.users().messages().send(userId="me", body=body_payload).execute()
        print(f"Success: Email sent to {to_email}. Message ID: {send_message['id']}")
        return True

    except HttpError as error:
        print(f"Error sending email via Gmail API: {error}")
        return False
    except Exception as e:
        print(f"Unexpected error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send an email via Gmail API (OAuth2)")
    parser.add_argument("--setup", action="store_true", help="Perform initial OAuth browser setup")
    parser.add_argument("--to", help="Recipient email address")
    parser.add_argument("--subject", help="Email subject line")
    parser.add_argument("--body", help="Email HTML or Text body")

    args = parser.parse_args()

    if args.setup:
        creds = load_credentials()
        if creds and creds.valid:
            print("Successfully authenticated and generated token.json!")
    elif args.to and args.subject and args.body:
        send_email(args.to, args.subject, args.body)
    else:
        print("Error: --to, --subject, and --body are required unless running with --setup")

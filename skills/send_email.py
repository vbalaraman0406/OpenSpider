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
        # Outer wrapper with visible border
        out = '<table style="width:100%;border-collapse:collapse;margin:20px 0;font-size:13.5px;border:1px solid #3a3a6a;border-radius:8px;overflow:hidden;">\n'
        for idx, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip('|').split('|')]
            tag = 'th' if idx == 0 else 'td'
            # Header: indigo-blue bg, white bold text, bottom border
            style_header = ('background:#1e1e4a;color:#ffffff;padding:11px 14px;'
                            'text-align:left;border-bottom:2px solid #3a3a6a;'
                            'font-weight:700;font-size:13px;border-right:1px solid #3a3a6a;')
            # Even data rows slightly lighter for contrast
            bg_even = '#16162a'
            bg_odd  = '#0d0d1a'
            bg = bg_even if idx % 2 == 0 else bg_odd
            style_cell = (f'background:{bg};padding:10px 14px;'
                          'border-bottom:1px solid #2a2a44;color:#c8c8d8;'
                          'border-right:1px solid #2a2a44;font-size:13px;')
            out += f'<tr>'
            for cell in cells:
                st = style_header if idx == 0 else style_cell
                display_cell = weather_emoji_inject(cell) if idx > 0 else cell
                out += f'<{tag} style="{st}">{inline_format(display_cell)}</{tag}>'
            out += '</tr>\n'
        out += '</table>\n'
        table_rows = []
        in_table = False
        return out

    # Weather condition keyword → emoji prefix map (order from most specific to least)
    WEATHER_EMOJI_MAP = [
        (r'\bThunderstorm(s)?\b',       '⛈️'),
        (r'\bHeavy Rain\b',             '🌧️'),
        (r'\bRain (Likely|Showers)\b',  '🌧️'),
        (r'\bRainy\b',                  '🌧️'),
        (r'\bRain\b',                   '🌦️'),
        (r'\bDrizzle\b',               '🌦️'),
        (r'\bSnow Showers\b',           '🌨️'),
        (r'\bSnow\b',                   '❄️'),
        (r'\bBlizzard\b',               '🌨️'),
        (r'\bSleet\b',                  '🌨️'),
        (r'\bFog\b',                    '🌫️'),
        (r'\bHaz[ey]\b',               '🌫️'),
        (r'\bSmoke\b',                  '🌫️'),
        (r'\bPartly (Cloudy|Sunny)\b',  '⛅'),
        (r'\bMostly Cloudy\b',          '🌥️'),
        (r'\bCloudy\b',                 '☁️'),
        (r'\bOvercast\b',               '☁️'),
        (r'\bMostly Sunny\b',           '🌤️'),
        (r'\bPartly Sunny\b',           '🌤️'),
        (r'\bSunny\b',                  '☀️'),
        (r'\bClear\b',                  '🌙'),
        (r'\bWindy\b',                  '💨'),
        (r'\bBreezy\b',                 '🌬️'),
        (r'\bHail\b',                   '🌩️'),
        (r'\bTornado\b',                '🌪️'),
    ]

    def weather_emoji_inject(text: str) -> str:
        """Prepend a weather emoji if the text matches a known weather condition."""
        for pattern, emoji in WEATHER_EMOJI_MAP:
            if re.search(pattern, text, re.IGNORECASE):
                if not text.startswith(emoji):
                    text = f'{emoji} {text}'
                break
        return text

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

        # Alert / callout lines — lines starting with ⚠️ 🚨 🔴 get a callout box
        ALERT_EMOJIS = ('⚠️', '🚨', '🔴', '‼️', '🛑', '❗')
        if any(stripped.startswith(e) for e in ALERT_EMOJIS):
            if in_list:
                html_lines.append(f'</ul>')
                in_list = False
            callout = ('<div style="background:#1a140a;border-left:4px solid #f59e0b;'
                       'border-radius:6px;padding:12px 16px;margin:12px 0;">'
                       '<p style="color:#fbbf24;font-size:13.5px;margin:0;line-height:1.6;">'
                       + inline_format(stripped) + '</p></div>')
            html_lines.append(callout)
            continue

        # Headers
        if stripped.startswith('######'):
            html_lines.append(f'<h6 style="color:#a5b4fc;font-size:13px;margin:12px 0 4px;font-weight:600;">{inline_format(stripped[6:].strip())}</h6>')
        elif stripped.startswith('#####'):
            html_lines.append(f'<h5 style="color:#a5b4fc;font-size:14px;margin:12px 0 4px;font-weight:600;">{inline_format(stripped[5:].strip())}</h5>')
        elif stripped.startswith('####'):
            html_lines.append(f'<h4 style="color:#c7d2fe;font-size:15px;margin:14px 0 6px;font-weight:600;">{inline_format(stripped[4:].strip())}</h4>')
        elif stripped.startswith('###'):
            # H3 — violet/indigo accent
            html_lines.append(f'<h3 style="color:#c4b5fd;font-size:16px;margin:20px 0 8px;font-weight:700;">{inline_format(stripped[3:].strip())}</h3>')
        elif stripped.startswith('##'):
            # H2 — orange-amber accent (main section headers like "🔥 Top Headlines")
            html_lines.append(f'<h2 style="color:#fb923c;font-size:18px;margin:28px 0 10px;font-weight:700;">{inline_format(stripped[2:].strip())}</h2>')
        elif stripped.startswith('#'):
            # H1 — large white (usually the report title in body)
            html_lines.append(f'<h1 style="color:#fff;font-size:22px;margin:24px 0 12px;font-weight:700;">{inline_format(stripped[1:].strip())}</h1>')
        # Numbered list
        elif re.match(r'^\d+\.\s', stripped):
            if not in_list:
                html_lines.append('<ol style="margin:8px 0;padding-left:24px;color:#c8c8d8;">')
                in_list = 'ol'
            list_text = re.sub(r'^\d+\.\s', '', stripped)
            html_lines.append(f'<li style="margin:5px 0;line-height:1.65;">{inline_format(list_text)}</li>')
        # Unordered list
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul style="margin:8px 0;padding-left:24px;color:#c8c8d8;">')
                in_list = 'ul'
            html_lines.append(f'<li style="margin:5px 0;line-height:1.65;">{inline_format(stripped[2:])}</li>')
        else:
            if in_list:
                html_lines.append(f'</{in_list}>')
                in_list = False
            # Regular paragraph
            if stripped:
                html_lines.append(f'<p style="color:#c8c8d8;line-height:1.75;margin:8px 0;font-size:14px;">{inline_format(stripped)}</p>')
            else:
                html_lines.append('')

    # Flush remaining table
    if in_table:
        html_lines.append(flush_table())
    if in_list:
        html_lines.append(f'</{in_list}>' if isinstance(in_list, str) else '</ul>')

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


def _extract_hero_from_body(html_body: str, subject: str) -> tuple[str, str]:
    """Extract the first <h1> from the body as the hero title. Returns (hero_title, remaining_html)."""
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_body, re.DOTALL)
    if h1_match:
        hero = h1_match.group(1).strip()
        remaining = html_body[:h1_match.start()] + html_body[h1_match.end():]
        return hero, remaining
    # Fall back to subject line, stripping leading emoji from subject for cleaner display
    clean_subject = re.sub(r'^[\U00010000-\U0010ffff\u2600-\u27ff\u1F300-\u1F9FF]+\s*', '', subject).strip()
    emoji_match = re.match(r'^([\U00010000-\U0010ffff\u2600-\u27ff\u1F300-\u1F9FF]+)', subject)
    hero_emoji = emoji_match.group(1) if emoji_match else ''
    hero = f'{hero_emoji} {clean_subject}' if hero_emoji else clean_subject
    return hero, html_body


def wrap_in_email_template(html_body: str, subject: str = '') -> str:
    """Wrap HTML content in the Option A premium dark-themed email template."""
    agent_name = get_agent_name()

    # Strip any LLM-generated outer HTML wrappers to prevent style conflicts
    html_body = re.sub(r'<!DOCTYPE[^>]*>', '', html_body, flags=re.IGNORECASE)
    html_body = re.sub(r'<html[^>]*>|</html>', '', html_body, flags=re.IGNORECASE)
    html_body = re.sub(r'<head[^>]*>.*?</head>', '', html_body, flags=re.IGNORECASE | re.DOTALL)
    html_body = re.sub(r'<body[^>]*>|</body>', '', html_body, flags=re.IGNORECASE)
    html_body = html_body.strip()

    # Extract H1 as hero title, use remainder as body
    hero_title, body_content = _extract_hero_from_body(html_body, subject)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#0a0a14;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0a0a14;">
<tr><td align="center" style="padding:24px 16px;">
<table role="presentation" width="640" cellspacing="0" cellpadding="0"
  style="max-width:640px;width:100%;background:#111127;border-radius:14px;
         border:1px solid #1e1e3a;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.5);">

<!-- ═══ HEADER BANNER ═══ -->
<tr>
<td style="background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%);padding:22px 32px;">
<table width="100%" cellspacing="0" cellpadding="0"><tr>
<td style="vertical-align:middle;">
  <span style="font-size:22px;font-weight:800;color:#fff;letter-spacing:-0.5px;">♾️ {agent_name}</span><br/>
  <span style="font-size:10.5px;color:#a5b4fc;letter-spacing:2px;text-transform:uppercase;font-weight:600;">Autonomous Agent Report</span>
</td>
<td align="right" style="vertical-align:top;">
  <span style="font-size:10px;color:#818cf8;background:rgba(30,27,75,0.8);
    padding:4px 12px;border-radius:20px;border:1px solid #4338ca;
    font-weight:600;letter-spacing:0.5px;">Automated</span>
</td>
</tr></table>
</td>
</tr>

<!-- ═══ HERO SECTION ═══ -->
<tr>
<td style="background:linear-gradient(180deg,#181830 0%,#0f0f22 100%);
           padding:28px 32px 24px;border-bottom:1px solid #1e1e3a;">
  <h1 style="margin:0;font-size:24px;font-weight:800;color:#ffffff;
            line-height:1.3;letter-spacing:-0.3px;">{hero_title}</h1>
</td>
</tr>

<!-- ═══ BODY CONTENT ═══ -->
<tr>
<td style="background:#0d0d1a;padding:28px 32px;">
{body_content}
</td>
</tr>

<!-- ═══ FOOTER ═══ -->
<tr>
<td style="background:#080812;padding:18px 32px;border-top:1px solid #1e1e3a;">
<table width="100%" cellspacing="0" cellpadding="0"><tr>
<td style="font-size:11px;color:#4a4a6a;line-height:1.6;">
  Powered by ♾️ <strong style="color:#6366f1;">{agent_name}</strong> — OpenSpider Agent System<br/>
  This is an automated message. Do not reply directly.
</td>
<td align="right" style="font-size:11px;color:#4a4a6a;white-space:nowrap;">
  🔒 Secure &nbsp;•&nbsp; 🤖 AI-Generated
</td>
</tr></table>
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

def send_email(to_email, subject, body, from_email=None):
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
        if from_email:
            message['From'] = from_email
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
    parser.add_argument("--from", dest="from_email", help="Sender email address (must be a verified Gmail alias)")

    args = parser.parse_args()

    if args.setup:
        creds = load_credentials()
        if creds and creds.valid:
            print("Successfully authenticated and generated token.json!")
    elif args.to and args.subject and args.body:
        send_email(args.to, args.subject, args.body, from_email=args.from_email)
    else:
        print("Error: --to, --subject, and --body are required unless running with --setup")

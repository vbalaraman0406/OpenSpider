#!/usr/bin/env python3
"""
linkedin_post.py — LinkedIn Post Skill for OpenSpider

Usage:
  python3 linkedin_post.py --draft "Your post text here"
  python3 linkedin_post.py --post
  python3 linkedin_post.py --status
  python3 linkedin_post.py --help

Actions:
  --draft TEXT   Save a draft post to workspace/linkedin_draft.json for approval.
                 The agent should send this to the user via WhatsApp for review.
  --post         Publish the approved draft to LinkedIn via the gateway API.
  --status       Check LinkedIn connection status and current draft.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

WORKSPACE = os.path.join(os.getcwd(), 'workspace')
DRAFT_FILE = os.path.join(WORKSPACE, 'linkedin_draft.json')
API_BASE = f"http://localhost:{os.environ.get('PORT', '4001')}"
API_KEY = os.environ.get('DASHBOARD_API_KEY', '')


def api_request(path: str, method: str = 'GET', data: dict = None) -> dict:
    """Make an authenticated API request to the gateway."""
    url = f"{API_BASE}{path}"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
    }
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        return {'error': f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {'error': str(e)}


def save_draft(text: str):
    """Save a post draft for user approval."""
    os.makedirs(WORKSPACE, exist_ok=True)
    draft = {
        'text': text,
        'created_at': __import__('datetime').datetime.now().isoformat(),
        'status': 'pending_approval',
        'char_count': len(text),
    }
    with open(DRAFT_FILE, 'w') as f:
        json.dump(draft, f, indent=2)

    print(f"✅ Draft saved ({len(text)} chars)")
    print(f"📋 Draft preview:")
    print(f"---")
    print(text[:500])
    if len(text) > 500:
        print(f"... [{len(text) - 500} more chars]")
    print(f"---")
    print(f"⚠️ IMPORTANT: Send this draft to the user via WhatsApp for approval before posting!")
    print(f"After user approves, run: python3 linkedin_post.py --post")


def publish_post():
    """Publish the approved draft to LinkedIn."""
    if not os.path.exists(DRAFT_FILE):
        print("❌ No draft found. Create one first with --draft")
        sys.exit(1)

    with open(DRAFT_FILE, 'r') as f:
        draft = json.load(f)

    if draft.get('status') == 'published':
        print("⚠️ This draft was already published. Create a new draft with --draft")
        sys.exit(1)

    text = draft.get('text', '')
    if not text:
        print("❌ Draft text is empty.")
        sys.exit(1)

    print(f"📤 Publishing to LinkedIn ({len(text)} chars)...")
    result = api_request('/api/linkedin/post', method='POST', data={'text': text})

    if result.get('error'):
        print(f"❌ Failed to publish: {result['error']}")
        sys.exit(1)

    if result.get('success'):
        # Update draft status
        draft['status'] = 'published'
        draft['published_at'] = __import__('datetime').datetime.now().isoformat()
        draft['post_id'] = result.get('postId', 'unknown')
        with open(DRAFT_FILE, 'w') as f:
            json.dump(draft, f, indent=2)

        print(f"✅ Successfully posted to LinkedIn!")
        print(f"📎 Post ID: {result.get('postId', 'unknown')}")
    else:
        print(f"❌ Unexpected response: {json.dumps(result)}")


def check_status():
    """Check LinkedIn connection status and current draft."""
    result = api_request('/api/linkedin/status')
    print("🔗 LinkedIn Connection Status:")
    if result.get('authenticated'):
        print(f"  ✅ Connected as: {result.get('name', 'Unknown')}")
        print(f"  ⏳ Token expires in: {result.get('expiresIn', 'unknown')}")
    else:
        print(f"  ❌ Not connected. Visit {API_BASE}/api/linkedin/auth to authenticate.")

    if os.path.exists(DRAFT_FILE):
        with open(DRAFT_FILE, 'r') as f:
            draft = json.load(f)
        print(f"\n📝 Current Draft:")
        print(f"  Status: {draft.get('status', 'unknown')}")
        print(f"  Length: {draft.get('char_count', 0)} chars")
        print(f"  Preview: {draft.get('text', '')[:100]}...")
    else:
        print(f"\n📝 No draft on file.")


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Post Skill for OpenSpider')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--draft', type=str, help='Save a draft post for approval')
    group.add_argument('--post', action='store_true', help='Publish the approved draft to LinkedIn')
    group.add_argument('--status', action='store_true', help='Check connection status and current draft')

    args = parser.parse_args()

    if args.draft:
        save_draft(args.draft)
    elif args.post:
        publish_post()
    elif args.status:
        check_status()


if __name__ == '__main__':
    main()

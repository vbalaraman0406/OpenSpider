# skills/canva_list_templates.py
# Lists available brand templates from the user's Canva account via the Connect API.
# Requires a one-time OAuth setup: python3 skills/canva_auth.py --setup

import os, sys, json, argparse
import requests

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(__file__))
from canva_auth import get_access_token

API_BASE = "https://api.canva.com/rest/v1"

def _auth_headers() -> dict:
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }

def list_templates(query: str = "", limit: int = 20) -> str:
    """
    Fetches the user's brand templates from the Canva Connect API.
    Optionally filters by a search query string.
    """
    params: dict = {"limit": min(limit, 50)}
    if query:
        params["query"] = query

    resp = requests.get(
        f"{API_BASE}/brand-templates",
        headers=_auth_headers(),
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    items = data.get("items") or data.get("brand_templates") or []
    templates = []
    for item in items:
        templates.append({
            "id":          item.get("id", ""),
            "name":        item.get("title", item.get("name", "Untitled")),
            "type":        item.get("type", "unknown"),
            "thumbnail":   item.get("thumbnail", {}).get("url", ""),
            "create_url":  item.get("url", ""),
        })

    return json.dumps({"status": "success", "count": len(templates), "templates": templates}, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List Canva brand templates.")
    parser.add_argument("--query", default="", help="Optional search query to filter templates")
    parser.add_argument("--limit", type=int, default=20, help="Max number of templates to return")
    args = parser.parse_args()
    print(list_templates(args.query, args.limit))

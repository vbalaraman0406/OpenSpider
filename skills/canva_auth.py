# skills/canva_auth.py
# Shared Canva OAuth 2.0 helper — used by all Canva skill scripts.
# Uses Authorization Code flow: first call `get_auth_url()` to get a user
# authorization URL, then after the user grants access exchange the code
# for tokens with `exchange_code_for_token()`. Subsequent calls use the
# saved refresh token to silently refresh access.

import os
import base64
import hashlib
import json
import secrets
import time
import urllib.parse
import requests

CANVA_TOKEN_URL  = "https://api.canva.com/rest/v1/oauth/token"
CANVA_AUTH_URL   = "https://www.canva.com/api/oauth/authorize"
TOKEN_CACHE_PATH = os.path.join(os.path.dirname(__file__), ".canva_token_cache.json")
PKCE_CACHE_PATH  = os.path.join(os.path.dirname(__file__), ".canva_pkce_cache.json")

def _client_id() -> str:
    v = os.getenv("CANVA_CLIENT_ID", "")
    if not v:
        raise RuntimeError("CANVA_CLIENT_ID is not set in environment / .env")
    return v

def _client_secret() -> str:
    v = os.getenv("CANVA_CLIENT_SECRET", "")
    if not v:
        raise RuntimeError("CANVA_CLIENT_SECRET is not set in environment / .env")
    return v

def _basic_auth_header() -> str:
    """Build the Base64-encoded Basic Auth header value."""
    raw = f"{_client_id()}:{_client_secret()}"
    return "Basic " + base64.b64encode(raw.encode()).decode()

# ---------------------------------------------------------------------------
# PKCE helpers (S256 — required by Canva)
# ---------------------------------------------------------------------------

def _generate_pkce_pair() -> tuple[str, str]:
    """Return (code_verifier, code_challenge) using S256 method."""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge

def _save_pkce(verifier: str):
    with open(PKCE_CACHE_PATH, "w") as f:
        json.dump({"code_verifier": verifier}, f)

def _load_pkce() -> str:
    if os.path.exists(PKCE_CACHE_PATH):
        return json.loads(open(PKCE_CACHE_PATH).read()).get("code_verifier", "")
    return ""

# ---------------------------------------------------------------------------
# Token cache helpers
# ---------------------------------------------------------------------------

def _load_cache() -> dict:
    if os.path.exists(TOKEN_CACHE_PATH):
        try:
            return json.loads(open(TOKEN_CACHE_PATH).read())
        except Exception:
            pass
    return {}

def _save_cache(data: dict):
    with open(TOKEN_CACHE_PATH, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_auth_url(redirect_uri: str, scopes: list[str], state: str = "openspider") -> tuple[str, str]:
    """
    Step 1 (one-time setup): Return (auth_url, code_verifier).
    The code_verifier must be stored and sent during token exchange.
    """
    code_verifier, code_challenge = _generate_pkce_pair()
    _save_pkce(code_verifier)

    params = {
        "response_type":         "code",
        "client_id":             _client_id(),
        "redirect_uri":          redirect_uri,
        "scope":                 " ".join(scopes),
        "state":                 state,
        "code_challenge_method": "s256",
        "code_challenge":        code_challenge,
    }
    return CANVA_AUTH_URL + "?" + urllib.parse.urlencode(params), code_verifier


def exchange_code_for_token(code: str, redirect_uri: str) -> dict:
    """
    Step 2 (one-time): Exchange the authorization code for access + refresh tokens.
    Loads the saved code_verifier automatically.
    """
    code_verifier = _load_pkce()
    if not code_verifier:
        raise RuntimeError("No PKCE verifier found. Re-run --setup to start a fresh auth flow.")

    resp = requests.post(
        CANVA_TOKEN_URL,
        headers={
            "Authorization": _basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type":    "authorization_code",
            "code":          code,
            "redirect_uri":  redirect_uri,
            "code_verifier": code_verifier,
        },
        timeout=15,
    )
    if not resp.ok:
        print(f"❌ Token exchange failed ({resp.status_code}): {resp.text}")
    resp.raise_for_status()
    data = resp.json()
    data["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
    _save_cache(data)
    return data


def get_access_token() -> str:
    """
    Returns a valid access token, refreshing automatically if expired.
    Raises RuntimeError if no token is cached (run exchange_code_for_token first).
    """
    cache = _load_cache()
    if not cache:
        raise RuntimeError(
            "No Canva token found. Run `python3 skills/canva_auth.py --setup` "
            "and follow the OAuth flow first."
        )

    # Refresh if expired
    if time.time() >= cache.get("expires_at", 0):
        refresh_token = cache.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("Canva token expired and no refresh token found. Re-run OAuth setup.")

        resp = requests.post(
            CANVA_TOKEN_URL,
            headers={
                "Authorization": _basic_auth_header(),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type":    "refresh_token",
                "refresh_token": refresh_token,
            },
            timeout=15,
        )
        resp.raise_for_status()
        new_data = resp.json()
        new_data["expires_at"] = time.time() + new_data.get("expires_in", 3600) - 60
        _save_cache(new_data)
        return new_data["access_token"]

    return cache["access_token"]


# ---------------------------------------------------------------------------
# CLI one-time setup wizard
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse, webbrowser

    parser = argparse.ArgumentParser(description="Canva OAuth one-time setup")
    parser.add_argument("--setup", action="store_true", help="Run interactive OAuth setup")
    parser.add_argument("--redirect", default="http://localhost:9999/callback", help="Redirect URI registered in Canva")
    args = parser.parse_args()

    if args.setup:
        scopes = [
            "design:content:read",
            "design:content:write",
            "asset:read",
            "asset:write",
            "brandtemplate:content:read",
            "brandtemplate:meta:read",
        ]
        url, _ = get_auth_url(args.redirect, scopes)
        print("\n🔗 Open this URL in your browser and authorize the OpenSpider app:\n")
        print(url)
        print()
        webbrowser.open(url)
        raw = input("✏️  Paste the full redirect URL (or just the 'code' value): ").strip()
        # Auto-extract code from a full URL if pasted
        if raw.startswith("http"):
            parsed = urllib.parse.urlparse(raw)
            code = urllib.parse.parse_qs(parsed.query).get("code", [raw])[0]
        else:
            code = raw
        result = exchange_code_for_token(code, args.redirect)
        print(f"\n✅ Tokens saved! Access token expires in {result.get('expires_in', '?')}s")
    else:
        parser.print_help()

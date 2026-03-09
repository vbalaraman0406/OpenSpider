# skills/canva_generate_video.py
# Uploads a video asset to the user's Canva account, optionally populating
# a brand template via the Autofill API if a video template_id is provided.
# Otherwise just uploads and returns the asset ID / URL.
# Requires a one-time OAuth setup: python3 skills/canva_auth.py --setup

import os, sys, json, time, argparse, mimetypes, base64
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

def _auth_headers(content_type: str = "application/json") -> dict:
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": content_type,
    }

def upload_asset(file_path: str, display_name: str = "") -> dict:
    """
    Uploads a local image/video file to the user's Canva media library.
    Returns the Canva asset object (id, name, thumbnail, etc.).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    mime, _ = mimetypes.guess_type(file_path)
    mime = mime or "application/octet-stream"
    name = (display_name or os.path.basename(file_path))[:50]

    # Canva requires: Content-Type=octet-stream + Asset-Upload-Metadata header
    # with {"name_base64": base64(name)}
    name_b64 = base64.b64encode(name.encode()).decode()
    metadata_header = json.dumps({"name_base64": name_b64})

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    resp = requests.post(
        f"{API_BASE}/asset-uploads",
        headers={
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/octet-stream",
            "Asset-Upload-Metadata": metadata_header,
        },
        data=file_bytes,
        timeout=120,
    )
    resp.raise_for_status()
    job_id = resp.json().get("job", {}).get("id", "")
    if not job_id:
        raise RuntimeError(f"No job ID returned from Canva upload: {resp.text}")

    # Poll for completions
    for _ in range(15):
        time.sleep(2)
        poll = requests.get(
            f"{API_BASE}/asset-uploads/{job_id}",
            headers={"Authorization": f"Bearer {get_access_token()}"},
            timeout=30,
        )
        poll.raise_for_status()
        data = poll.json()
        status = data.get("job", {}).get("status", "")
        if status in ("success", "complete", "completed"):
            return data.get("job", {}).get("asset", {})
        if status in ("failed", "error"):
            raise RuntimeError(f"Canva asset upload failed: {data}")

    raise TimeoutError("Canva asset upload timed out.")


def generate_video(template_id: str, assets: dict) -> str:
    """
    If a template_id is given, runs an autofill job with video assets.
    Otherwise, uploads the first asset URL directly and returns an asset link.
    """
    print(f"🎥 [Canva API] Generating video with template '{template_id}'...")

    if template_id and template_id != "none":
        # Build autofill data from asset dict
        data: dict = {}
        for field, url in assets.items():
            data[field] = {"type": "image", "asset_url": url}  # Canva accepts video URLs here too

        payload = {
            "brand_template_id": template_id,
            "data": data,
        }
        resp = requests.post(
            f"{API_BASE}/autofills",
            headers=_auth_headers(),
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        job = resp.json()
        job_id = job.get("job", {}).get("id") or job.get("id")

        for _ in range(20):
            time.sleep(3)
            poll = requests.get(f"{API_BASE}/autofills/{job_id}", headers=_auth_headers(), timeout=30)
            poll.raise_for_status()
            sd = poll.json()
            status = sd.get("job", {}).get("status") or sd.get("status", "")
            if status in ("success", "complete", "completed"):
                design = sd.get("job", {}).get("result", {}).get("design") or sd.get("result", {}).get("design", {})
                design_id  = design.get("id", "")
                design_url = design.get("url", f"https://www.canva.com/design/{design_id}/edit")
                return json.dumps({"status": "success", "message": "Video design created.", "url": design_url, "format": "canva_design"}, indent=2)
            if status in ("failed", "error"):
                return json.dumps({"status": "error", "message": "Canva video job failed.", "raw": sd})

        return json.dumps({"status": "timeout", "message": "Video autofill timed out.", "job_id": job_id})

    # No template — just report the assets
    return json.dumps({
        "status": "success",
        "message": "Assets ready. Upload local files using upload_asset() or attach URLs directly in a Canva design.",
        "assets": assets,
    }, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video using a Canva template.")
    parser.add_argument("--template_id", default="none", help="Canva brand video template ID (or 'none')")
    parser.add_argument("--assets", default="{}", help="JSON string mapping template fields to video/image URLs")
    args = parser.parse_args()
    print(generate_video(args.template_id, json.loads(args.assets)))

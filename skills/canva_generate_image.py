# skills/canva_generate_image.py
# Generates an image using the Canva Autofill API.
# Requires a one-time OAuth setup: python3 skills/canva_auth.py --setup

import os, sys, json, time, argparse
import requests

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

# Add skills directory to path for shared auth module
sys.path.insert(0, os.path.dirname(__file__))
from canva_auth import get_access_token

API_BASE = "https://api.canva.com/rest/v1"

def _auth_headers() -> dict:
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }

def get_brand_template_dataset(template_id: str) -> dict:
    """Fetch the list of autofillable fields for a given brand template."""
    resp = requests.get(
        f"{API_BASE}/brand-templates/{template_id}/dataset",
        headers=_auth_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

def generate_image(template_id: str, text_vars: dict, image_vars: dict) -> str:
    """
    Creates a design autofill job on the Canva API and polls until complete.
    Returns a JSON string with the resulting design URL.
    """
    print(f"🎨 [Canva API] Generating image from template '{template_id}'...")

    # Build data payload for autofill
    data: dict = {}
    for field, value in text_vars.items():
        data[field] = {"type": "text", "text": value}
    for field, url in image_vars.items():
        data[field] = {"type": "image", "asset_url": url}

    payload = {
        "brand_template_id": template_id,
        "data": data,
    }

    # POST to create the autofill job
    resp = requests.post(
        f"{API_BASE}/autofills",
        headers=_auth_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    job = resp.json()
    job_id = job.get("job", {}).get("id") or job.get("id")
    if not job_id:
        return json.dumps({"status": "error", "message": "No job ID returned from Canva.", "raw": job})

    print(f"   Job created: {job_id}. Polling for completion...")

    # Poll GET /autofills/{jobId} until done (max 60 s)
    for _ in range(20):
        time.sleep(3)
        poll = requests.get(
            f"{API_BASE}/autofills/{job_id}",
            headers=_auth_headers(),
            timeout=30,
        )
        poll.raise_for_status()
        status_data = poll.json()
        status = (
            status_data.get("job", {}).get("status")
            or status_data.get("status", "")
        )

        if status in ("success", "complete", "completed"):
            design = (
                status_data.get("job", {}).get("result", {}).get("design")
                or status_data.get("result", {}).get("design", {})
            )
            design_id  = design.get("id", "")
            design_url = design.get("url", f"https://www.canva.com/design/{design_id}/edit")
            result = {
                "status": "success",
                "message": "Image generated successfully via Canva Autofill API.",
                "design_id": design_id,
                "url": design_url,
            }
            return json.dumps(result, indent=2)

        if status in ("failed", "error"):
            return json.dumps({"status": "error", "message": f"Canva job failed.", "raw": status_data})

    return json.dumps({"status": "timeout", "message": "Canva autofill job timed out after 60 seconds.", "job_id": job_id})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an image using a Canva brand template.")
    parser.add_argument("--template_id", required=True, help="Canva brand template ID")
    parser.add_argument("--text",   default="{}", help="JSON string of text fields")
    parser.add_argument("--images", default="{}", help="JSON string of image field URLs")
    args = parser.parse_args()
    print(generate_image(args.template_id, json.loads(args.text), json.loads(args.images)))

import json, os, sys

# Current data extracted from the context
current = {
    "usa": {
        "status": "No problems at BMO Harris",
        "reports": 0,
        "top5": [
            {"issue": "Online Banking", "pct": "39%"},
            {"issue": "Login", "pct": "28%"},
            {"issue": "App", "pct": "16%"},
            {"issue": "Funds Transfer", "pct": "11%"},
            {"issue": "Mobile Banking", "pct": "6%"}
        ],
        "spikes_24h": False
    },
    "canada": {
        "status": "No problems at BMO Harris",
        "reports": 0,
        "top5": [
            {"issue": "Online Banking", "pct": "39%"},
            {"issue": "Login", "pct": "28%"},
            {"issue": "App", "pct": "16%"},
            {"issue": "Funds Transfer", "pct": "11%"},
            {"issue": "Mobile Banking", "pct": "6%"}
        ],
        "spikes_24h": False
    },
    "timestamp": "2026-03-18T09:29:00-07:00"
}

# Read last known state
last_file = "workspace/bmo_downdetector_last.json"
last = None
if os.path.exists(last_file):
    with open(last_file, 'r') as f:
        last = json.load(f)

# Compare
changes_detected = False
change_reasons = []

if last is None:
    # First run ever - no comparison possible, just save
    change_reasons.append("First run - no previous data to compare")
    # Don't flag as meaningful change for alerting on first run with no problems
    changes_detected = False
else:
    for region, label in [("usa", "USA"), ("canada", "Canada")]:
        old = last.get(region, {})
        new = current[region]
        
        # Status change
        old_status = old.get("status", "")
        new_status = new["status"]
        if old_status != new_status:
            changes_detected = True
            change_reasons.append(f"{label} status changed: '{old_status}' -> '{new_status}'")
        
        # Report count spike
        old_reports = old.get("reports", 0)
        new_reports = new["reports"]
        if new_reports > 50 or (old_reports > 0 and new_reports > old_reports * 2):
            changes_detected = True
            change_reasons.append(f"{label} report spike: {old_reports} -> {new_reports}")
        
        # Top 5 changes
        old_top5 = [x.get("issue", "") for x in old.get("top5", [])]
        new_top5 = [x["issue"] for x in new["top5"]]
        if old_top5 != new_top5:
            changes_detected = True
            change_reasons.append(f"{label} top 5 issues changed: {old_top5} -> {new_top5}")
        
        # Spike detection
        if new.get("spikes_24h") and not old.get("spikes_24h"):
            changes_detected = True
            change_reasons.append(f"{label} new 24h spike detected")

# Save current state
os.makedirs("workspace", exist_ok=True)
with open(last_file, 'w') as f:
    json.dump(current, f, indent=2)

# Output decision
result = {
    "changes_detected": changes_detected,
    "reasons": change_reasons,
    "should_send_whatsapp": changes_detected
}
print(json.dumps(result, indent=2))

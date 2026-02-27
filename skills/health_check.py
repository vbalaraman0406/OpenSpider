import os
import sys
import time
import platform
from datetime import datetime, timezone

def health_check():
    results = []
    all_ok = True

    # 1. Log current timestamp
    now = datetime.now(timezone.utc)
    results.append(f"[TIMESTAMP] Current UTC time: {now.isoformat()}")

    # 2. Verify workspace is accessible
    cwd = os.getcwd()
    workspace_readable = os.access(cwd, os.R_OK)
    workspace_writable = os.access(cwd, os.W_OK)
    results.append(f"[WORKSPACE] Current directory: {cwd}")
    results.append(f"[WORKSPACE] Readable: {workspace_readable}, Writable: {workspace_writable}")
    if not workspace_readable:
        all_ok = False

    # 3. List files in workspace (top-level)
    try:
        entries = os.listdir(cwd)
        results.append(f"[WORKSPACE] Files/dirs in workspace: {len(entries)}")
        if entries:
            results.append(f"[WORKSPACE] Sample entries: {entries[:10]}")
    except Exception as e:
        results.append(f"[WORKSPACE] ERROR listing directory: {e}")
        all_ok = False

    # 4. System info
    results.append(f"[SYSTEM] Platform: {platform.platform()}")
    results.append(f"[SYSTEM] Python version: {sys.version}")
    results.append(f"[SYSTEM] Node: {platform.node()}")

    # 5. Disk check (basic)
    try:
        statvfs = os.statvfs(cwd)
        free_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
        total_gb = (statvfs.f_blocks * statvfs.f_frsize) / (1024**3)
        results.append(f"[DISK] Free: {free_gb:.2f} GB / Total: {total_gb:.2f} GB")
    except Exception as e:
        results.append(f"[DISK] Could not check disk: {e}")

    # 6. Summary
    status = "HEALTHY" if all_ok else "DEGRADED"
    results.append(f"[STATUS] Overall system health: {status}")
    results.append(f"[CRON] Background cron trigger executed successfully.")

    return "\n".join(results)

if __name__ == "__main__":
    print(health_check())

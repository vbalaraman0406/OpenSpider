# Long Term Memory

Record enduring facts, system quirks, or important constraints discovered during operation here.

## System Architecture Facts

- **Cron jobs are PERSISTED to disk** at `workspace/cron_jobs.json`. They survive restarts. NEVER tell the user they are "in-memory only."
- **Scheduler heartbeat** runs every 60 seconds. It reads `cron_jobs.json` on each tick to check for due jobs.
- **Worker Agents have tools**: `send_whatsapp`, `send_email`, `browse_web`, `run_command`, `write_script`, `execute_script`, `schedule_task`, `message_agent`, `final_answer`.
- **Only Workers have tools** — if a task needs to send a message, email, browse the web, or execute code, it MUST be delegated to a Worker. The Manager's `direct_response` does NOT execute any tools.
- **WhatsApp messages** are sent natively via `send_whatsapp` tool. No external APIs (Twilio, Meta API) are needed.
- **Emails** are sent natively via `send_email` tool using OAuth-authenticated Gmail.
- **Agent configs** are stored at `workspace/agents/<role>/` with files: `SOUL.md`, `IDENTITY.md`, `CAPABILITIES.json`, `HEARTBEAT.md`.
- **Memory system**: `workspace/memory.md` = long-term facts. `workspace/memory/YYYY-MM-DD.md` = daily conversation log.

## User Preferences

- CEO/Owner: Vishnu Balaraman (coolvishnu@gmail.com)
- Preferred communication: WhatsApp + Email
- Email for notifications: coolvishnu@gmail.com

# OpenSpider Handover Document

Welcome to the OpenSpider repository! This document serves as a transition guide for incoming AI agents or developers. It summarizes the current state of the architecture (specifically the recent V2 implementations) and outlines pending logical next steps.

## Current Architecture (V2)

OpenSpider is a hierarchical, autonomous multi-agent system written in TypeScript (Node.js backend, React frontend). It communicates primarily through WhatsApp (via Baileys) and a local WebSocket dashboard.

### 1. The Memory System (`src/memory.ts`)
Agents are no longer amnesiac. We implemented an OpenClaw-inspired `workspace/` context architecture:
- **`workspace/SOUL.md`**: Defines the central agent's identity, personality, and operational boundaries.
- **`workspace/USER.md`**: Facts and preferences about the user.
- **`workspace/memory.md`**: Long-term durable facts.
- **`workspace/memory/YYYY-MM-DD.md`**: Daily conversational interaction logs.
- *How it works*: The `ManagerAgent` intercepts these files and prepends them to the LLM system prompt on every execution.

### 2. The Heartbeat Scheduler (`src/scheduler.ts`)
OpenSpider has a background `setInterval` loop that triggers every 60 seconds.
- It reads scheduled tasks from `workspace/cron_jobs.json`.
- When an interval hits, it dispatches a background command to the `ManagerAgent` to process the job autonomously.

### 3. The Dashboard UI (`dashboard/src/App.tsx`)
- **WebSockets**: The dashboard connects to `ws://localhost:4000` to stream real-time logs and trace agent execution steps.
- **Agent Flow Graph**: Uses Mermaid.js to cleanly draw sequential and parallel task executions.
- **Cron Jobs View**: A sleek, dark-mode, card-based UI (matching OpenClaw's aesthetic) that allows users to create, view, edit (enable/disable), manually run, and delete background tasks.

### 4. Setup & Management
- Run `npm run onboard` to launch a CLI wizard.
- Run `npm run start` to boot the PM2 background daemon.
- Run `openspider dashboard` from the CLI to automatically pop open the React Web UI in the default browser.

---

## Pending Work & Next Horizons

The context window for the previous session grew too large, so we are handing off the following feature ideas for the next iteration:

### 1. Expanded Skill Management
- Currently, users can generate Python script skills dynamically via the dashboard (`/api/skills/generate`).
- **Next Step**: Build UI views to *Edit* the raw Python code of these skills directly within the dashboard.

### 2. Deep Dive: Tool Execution Safety
- The system supports arbitrary command execution.
- **Next Step**: Enforce stricter sandboxing for `execute_command`. Currently, it heavily relies on the LLM adhering to instructions in `SOUL.md`. Adding a robust dry-run or verification middleware layer would be safer.

### 3. Agent Communication Sub-Channels
- Currently, the `ManagerAgent` coordinates the `WorkerAgent`s.
- **Next Step**: Allow `WorkerAgent`s to communicate with *each other* sequentially. (e.g., A Researcher passing data to a Writer without routing back through the Manager).

### 4. WhatsApp Media Support
- The WhatsApp gateway handles inbound strings well.
- **Next Step**: Handle inbound pictures, parse them via Vision models (Gemini/Claude), and formulate contextual responses.

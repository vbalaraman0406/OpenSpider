# OpenSpider Handoff Document

This document serves as a comprehensive context summary for the next agent picking up the development of the **OpenSpider** framework.

## Project Overview

OpenSpider is an autonomous, hierarchical multi-agent system designed to act aggressively and autonomously, executing tools without waiting for user permission unless absolutely necessary. It features a robust WhatsApp integration for remote control and an Apple-style, premium glassmorphic web dashboard for complete system visibility.

### Core Architecture
- **Language:** TypeScript/Node.js for both the backend engine and frontend dashboard.
- **Backend:** Express API serving the Dashboard and managing a native WebSocket (`ws`) layer for real-time telemetry, logs, and gateway status.
- **Frontend Dashboard:** A Vite + React web application (`dashboard/`) running on port `4000`.
- **LLM Engine:** A flexible inference engine (`src/llm/`) supporting OpenAI (GPT-4o) and internal custom providers (e.g., Antigravity-Internal).
- **Communication Channel:** An implemented `WhatsAppChannel` utilizing `whatsapp-web.js` with session persistence, falling back to a Terminal UI if WhatsApp is unconfigured/fails.
- **Agent Hierarchy:** 
    - `ManagerAgent`: The primary gateway that parses incoming channel messages and orchestrates workers.
    - `WorkerAgent`: Specialized agents spun up by the Manager to execute specific tasks (Python code execution, web searches) in isolated contexts.

---

## Completed Work (Phases 1-6)

### Phase 1: Core Engine & Gateway Foundation
- Setup the TypeScript project structure (`src/`, `dashboard/`).
- Implemented `AntigravityProvider` and `OpenAIProvider` for LLM inference.
- Created the core `Server` architecture handling Express API routes and WebSocket broadcasting.

### Phase 2: Multi-Channel Communication Layer
- Built the `WhatsAppChannel` for authenticating and receiving/sending remote messages.
- Created a robust Terminal UI (`cli-tui.ts`) fallback mechanism for local testing when WhatsApp isn't available. Both route to the `ManagerAgent`.

### Phase 3: Telemetry & Tracing
- Implemented a unified system logger that intercepts `console.log/warn/error` and broadcasts them as JSONL over WebSockets to the dashboard.
- Implemented Token Usage tracking metrics, streaming exact token counts and costs per completion to the dashboard. 

### Phase 4: Apple-Style Dashboard Overhaul
- Configured Vite + React with TailwindCSS for the dashboard.
- Implemented a premium, dark-mode, glassmorphic UI system (`backdrop-blur-xl`, `bg-slate-900/40`, colored glows).
- Rebuilt the landing experience into a multi-tab router with a sophisticated Sidebar.
- Completely redesigned the "Channels Manager" to show running channels (WhatsApp) as beautiful, animated cards.

### Phase 5: OpenClaw Feature Parity
Added five new dedicated views to achieve feature parity with the reference "OpenClaw" architecture:
- **Overview:** Gateway specs, connection strings, instances, and cron active queues.
- **Sessions:** Fine-grained log of active session keys and token tracking tables.
- **Agents:** Workspace to inspect `ManagerAgent` and `WorkerAgent` identity definitions and system prompts.
- **Skills:** Management grid of loaded tools (`web_search`, `run_python`).
- **Logs:** A JSONL telemetry tab with Trace/Debug/Info/Error severity switches and auto-tailing behavior.

### Phase 6: Interactive UI Components
- Wired up the **Agents Workspace** view with state management (`useState`) to allow selecting different agents (e.g., Gateway Architect vs. Data Analyst) from a list, instantly updating the right-hand details pane.
- Established a **Glassmorphic Modal Overlay** pattern for data entry. 
- Implemented the `+ Add Skill` button to trigger a sleek, blurred modal overlay containing an execution code editor instead of navigating away to a new page.

---

## Current State & Known Issues

- **Build Status:** The dashboard compiles successfully via `npm run build` and serves static assets from `dashboard/dist` via the Express server on port `4000`. 
- **API Wiring:** The dashboard views (Overview, Sessions, Agents, Skills) are largely populated with **mock data state/arrays** to establish the glassmorphic aesthetics and verify layouts. The UI looks incredible and interactions work, but it is not pulling actual live internal state from the Node.js backend yet.

---

## Pending Objectives (Next Steps)

For the next agent picking up this context, here is what needs to be accomplished to make OpenSpider a production-ready system:

1. **Connect Dashboard to Backend Live State:**
   - The React components in `dashboard/src/App.tsx` (like `AgentsView` and `SkillsView`) need to fetch real configuration data from the Express backend via REST (`/api/agents`, `/api/skills`) instead of using hardcoded mock arrays.
   - Wire the active session tables and overview stats to live system metrics.

2. **Implement Modal Business Logic:**
   - The newly created `+ Add Skill` modal only controls UI state. You need to implement the backend `POST` endpoint to actually save dynamically generated Python/Node code snippets to the file system or database.
   - Build a similar Glassmorphic Modal overlay for the "Create Agent" button in the Agents Workspace.

3. **Complete the Agentic Loop:**
   - Ensure the `ManagerAgent` logic correctly parses intent and dispatches to the `WorkerAgent`.
   - Ensure the `WorkerAgent` can natively read the dynamic skills loaded from the interface and execute them in a secure sandbox context.

4. **Testing workflows:**
   - Test an end-to-end flow: Send a message via WhatsApp -> Manager routes to Worker -> Worker executes a dynamic python script skill -> Result sends back via WhatsApp. All while the live traces are observable on the Dashboard Logs view.

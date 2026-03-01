# OpenSpider Development Handover

## Overview
This document serves as a technical continuity layer for the incoming AI Agent taking over the OpenSpider workspace.

The previous session (Feb 28) focused entirely on **Token Optimization**, **Dashboard Bug Fixes**, and **JSON Parity Hardening** to prevent rogue LLM hallucinations from crashing the Node.js backend. 

---

## 1. Latest Session Fixes & System Integrations

### 1.1 Chat UI Eviction Bug (`dashboard/src/App.tsx`)
- **The Problem:** The user noted that their entire Chat History disappeared the instant the Agent began typing deep research.
- **The Fix:** The React `setLogs` state was strictly retaining only the last 5,000 WebSocket events. During complex multi-source scraping, the backend Worker Agents spewed thousands of internal `type: 'log'` diagnostic updates via the WebSocket. This rapidly flushed out and completely evicted the actual historical chat messages from the `.slice(-4999)` array. We fixed this by expanding the slice buffer to `50,000` and forcefully ignoring hyper-repetitive telemetry logs (like `"Emulating human typing"`).

### 1.2 "Task completed without explicit result" Bug & Token Limit Expansion
- **The Problem:** The WorkerAgent was returning a useless generic summary instead of the fully comprehensive Markdown tables requested, simply because the JSON `result` key was missing.
- **The Fix (`src/llm/providers/AntigravityInternalProvider.ts`):** 
    1. The internal Provider API had a hardcoded `maxOutputTokens: 1500` config, which fatally amputated any rich markdown tables mid-generation. This was expanded to `8192`.
    2. The `jsonrepair` AST regex fallback parser was aggressively ignoring the `"result"` key while saving properties like `"thought"`. The `"result"` key string was added to the bypass dictionary.
    3. `WorkerAgent.ts` was patched with strict Self-Healing logic: If the LLM submits a `final_answer` without a `result` payload, it throws an internal exception to force the LLM to reiterate.

### 1.3 Chat Amnesia Reboot Bug (`src/server.ts`)
- **The Problem:** The `/api/chat/history` endpoint returned an empty array `[]` on browser refresh because `fs.readdirSync` couldn't find the memory files.
- **The Fix:** Removed a fatal double-escaped regex string (`\\d{4}` -> `\d{4}`) inside the chronological file merger, allowing Node to safely read `2026-03-01.md`.

---

## 2. Legacy Architecture Additions (V2)

### 2.1 Token Optimization & Context Pruning (V2)
- **The Problem:** The `WorkerAgent` was submitting exponential ~20,000+ token payloads to Anthropic/Google Gemini on iteration `25` because it was sending its entire historical Thought process and raw HTML stdout scrapes array.
- **The Fix (`src/agents/WorkerAgent.ts`):** We implemented "OpenClaw V2 Hard Pruning". 
    - At the start of every loop, the engine iterates backwards through the `messages` array.
    - If a turn is older than the `SLIDING_WINDOW_TURNS` (currently set to `2`), the engine dynamically parses the historic `assistant` JSON payload and **destructively skeletonizes it**.
    - It replaces massive `thought`, `content`, `command`, and `args` variables with memory pointers (e.g. `[PRUNED_BY_OPENCLAW_COMPACTION]`), dropping historic token drag to ~0 while retaining the logical sequence (`action: "web_search"`).
    - It also truncates raw `user` tool stdout results.

### 1.2 JSON Hallucination Hardening
- **The Problem:** Even with a pruned 1k prompt, the internal Antigravity IDE model would occasionally ignore the schema and write a massive 20,000-word essay about its `thought` process instead of actually executing the `run_command` action, which crashed the `JSON.parse()` wrapper with a SyntaxError.
- **The Fix (`src/llm/providers/AntigravityInternalProvider.ts`):** 
    - Reduced `maxOutputTokens` from `64000` down to `1500`.
    - Enforced `temperature: 0.1` to force deterministic adherence to the schema.
    - Ripped out the basic JSON parser and replaced it with a strict, multi-tier Regex extractor that explicitly isolates ````json ... ```` fenced blocks OR strictly bounded `{}` brackets, ignoring any trailing conversational hallucinations.

### 1.3 Dashboard React UI Fixes
- **The Auto-Scroll Bug (`dashboard/src/App.tsx`):** Injected `chatEndRef` and `scrollRef` DOM markers to trigger `scrollIntoView({ behavior: 'smooth' })` when `logs` arrays map new Agent messages.
- **The Timestamp Bug (`src/server.ts`):** The `/api/chat/history` endpoint was reading `[11:15:32 AM]` from the `memory.md` transcript and sending it raw. The React frontend couldn't parse it upon page refresh. Updated the Node server to prepend the current Date strings so they compile into valid ISO Date strings.
- **The Expense Bug (`src/usage.ts`):** Corrected the Pricing Matrix to attribute `$0.00` to the internal `claude-opus-4-6-thinking` model so it stops falsely generating fake expenses on the billing card.

---

## 2. Critical Environmental Warning (Port 4001)

- **The Issue:** The user accidentally executed the `openspider dashboard` CLI command in a separate background terminal window. This means the global installation of OpenSpider is locked onto server port `4001`.
- **The Symptoms:** Running `npm run dev` in this local workspace successfully launches Vite on port `5173`, but the backend will crash with `EADDRINUSE: :::4001`.
- **The Workaround Used:** Instead of fighting the background terminal, we ran `npm run build:frontend` to compile the local React `/dist/` bundle directly into the global OpenSpider instance so the user could see the UI fixes live. 
- **⚠️ NEXT STEPS:** To resume standard `npm run dev` local iterations, the user or the Incoming Agent MUST find the rogue background terminal window and `Ctrl+C` kill the global `openspider` command, or write a brute-force bash script to sever any process listening on TCP `4001`.

---

## 3. Pending Work / Roadmap

1. **Dynamic Sandboxing:** Further restrict the `run_command` permissions defined in `<AGENT>/CAPABILITIES.json`.
2. **Cron Jobs UI:** The previous agent began exploring the `cron_jobs.json` file. The frontend dashboard route for `/cron` has not been fully implemented.
3. **Agent Flow Graph Resilience:** Ensure the `/api/chat/history` logic correctly rehydrates the `AgentFlowGraph.tsx` nodes upon page refresh, not just the text logs.

*Godspeed.*

---
layout: home

hero:
  name: OpenSpider v2.0.1 🕷️
  text: Autonomous Multi-Agent System
  tagline: A self-hosted AI agent gateway for WhatsApp — with multi-agent orchestration, voice messages, scheduled tasks, and a beautiful web dashboard with dark/light themes.
  actions:
    - theme: brand
      text: Get Started →
      link: /getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/vbalaraman0406/OpenSpider

features:
  - icon: 🤖
    title: Multi-Agent Architecture
    details: A Manager agent orchestrates Worker agents (Coder, Researcher) using plan-delegate-execute workflows. Each agent has its own persona, capabilities, and tools.
  - icon: 💬
    title: WhatsApp Native
    details: Built on Baileys for native WhatsApp integration. Supports DM and group chats with per-group mention/listen modes and security allowlists.
  - icon: 🎤
    title: Voice Messages
    details: Send voice notes to OpenSpider — Whisper transcribes them locally. The agent replies with ElevenLabs-powered voice notes for a natural, voice-in voice-out experience.
  - icon: 🧠
    title: Multi-LLM Support
    details: Plug in any LLM — Google Gemini, Anthropic Claude, OpenAI, Ollama (local), or any OpenAI-compatible endpoint. Hot-swap models via configuration.
  - icon: 📊
    title: Web Dashboard
    details: Real-time dashboard with theme toggle (dark/light/system), health monitoring, Agent Chat with file attachments, Agent Flow visualization, Cron Jobs, and Usage analytics.
  - icon: ⏰
    title: Scheduled Tasks
    details: Agents can create and manage their own cron jobs. A 60-second heartbeat loop executes recurring tasks autonomously, with results displayed inline in the chat.
  - icon: 🛠️
    title: Extensible Tools
    details: Built-in tools for web search, web browsing (Playwright), email (Gmail OAuth), voice notes, file operations, and a dynamic skill system.
  - icon: 🎨
    title: Theme & Health
    details: Dashboard supports dark, light, and system theme modes. A live health indicator shows green/amber/red status for WhatsApp, LLM, and server components.
---

## What is OpenSpider?

OpenSpider is a **self-hosted, autonomous multi-agent system** designed to be your personal AI assistant via WhatsApp. Send a message, get an intelligent response powered by the LLM of your choice.

Unlike simple chatbots, OpenSpider uses a **hierarchical agent architecture**:

- A **Manager agent** (🧠 Ananta) receives your request, creates a plan, and delegates tasks
- **Worker agents** (⚡ Cipher the Coder, 🔮 Oracle the Researcher) execute specific tasks using specialized tools
- Results flow back through the Manager for a polished final response

### Key Capabilities

| Capability | Description |
|---|---|
| **Multi-agent orchestration** | Manager delegates to workers with parallel task execution |
| **WhatsApp messaging** | DM and group chat support with security controls |
| **Voice messages** | Voice-in (Whisper) and voice-out (ElevenLabs) via WhatsApp |
| **Web browsing** | Playwright-powered headless browser for research |
| **Email sending** | Gmail OAuth with professional HTML templates |
| **Task scheduling** | Cron-style scheduled tasks managed by agents |
| **Web dashboard** | Real-time monitoring, chat, and configuration UI |
| **Theme support** | Dark, light, and system-follow theme modes |
| **Health monitoring** | Green/amber/red health indicator with component status |
| **Multiple LLMs** | Google, Anthropic, OpenAI, Ollama, and custom providers |
| **CLI management** | Full CLI for setup, daemon control, and tooling |

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/vbalaraman/OpenSpider/main/install.sh | bash

# Configure
openspider onboard

# Start the gateway
openspider start

# Open the dashboard
openspider dashboard
```

[Get Started →](/getting-started)

# Changelog

All notable changes to OpenSpider will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [2.5.0] - 2026-04-01
### Added
- **Native WhatsApp Role-Based Access Control (RBAC)**: Added 'admin' and 'guest' roles to WhatsApp senders. Guests are tightly firewalled from utilizing host system tools like \`run_command\`, \`schedule_task\`, and \`execute_script\`.
- **Dashboard RBAC UI**: Upgraded the local web dashboard with strict Admin vs. Guest toggles for both Direct Messages and WhatsApp Group Chats. New contacts explicitly default to Guest.

## [2.4.0] - 2026-04-01
### Added
- **Global Message Deduplication**: Introduced Cryptographic Rolling Hash (SHA-256) at the lowest Node-level pipeline layers (WhatsApp + Gmail) to mathematically prevent bot looping and identical duplicate cron job delivery.
- **Native Chatbot Interaction**: Enforced the `type_and_enter` framework with built-in 4-second implicit delays mimicking human-typing speed to bypass Recaptcha blocks and improve robust completion rates on complex React state inputs.
- **Upgraded LLM Intelligence Routing**: Deployed `gemini-3.1-pro` into the unified failover capacity array as the primary backup to Claude Opuses.

### Fixed
- **LLM Outage Resilience**: Enhanced Internal IDE model API resiliency against `503 MODEL_CAPACITY_EXHAUSTED` outages on heavy endpoints.

## [2.3.1] - 2026-03-17
### Fixed
- **WhatsApp Group Messaging**: Upgraded Baileys from 6.17.16 to 7.0.0-rc.9 to fix group message delivery (LID-based group addressing)
- **Resilient Session Assertion**: Added `scripts/patch-baileys.js` to handle batch `assertSessions` failures gracefully (one-by-one fallback)
- **Group Send Retry Logic**: Retry path now uses resilient one-by-one session assertion instead of failing on first error
- WhatsApp send API now supports group JIDs with hyphenated format
- Group session refresh and sender-key cleanup before group sends
- WhatsApp contacts picker: DMs always visible, groups sort by exact match

### Added
- **WhatsApp Contacts Picker**: Cron job editor now has a contact/group selector
- Cron execution log persistence to disk
- `/release` workflow documentation

## [2.3.0] - 2026-03-16
### Added
- **Image & Video Vision Support**: Agent can now see and analyze images sent via WhatsApp (previously said "I cannot process images")
- **Video Thumbnail Extraction**: WhatsApp video messages have their thumbnails extracted and sent to the LLM for visual analysis
- **Vision Capability Declaration**: Agent identity explicitly declares multimodal vision capability
- **Image Passthrough to Workers**: Images are now forwarded from Manager to Worker agents, preventing hallucinated descriptions
- **Dynamic Skills UI Redesign**: Compact table-style list with readable names (was clipped card grid)
- **Cron Execution Logs Tab**: Dedicated section for viewing cron job execution results
- **Versioning System**: SemVer-based versioning with CHANGELOG.md, GitHub releases, and dashboard update banner
- **Update Available Banner**: Dashboard shows notification when a newer version is available on GitHub

### Fixed
- Chat message sort order (messages now display chronologically)
- Cron job logs no longer pollute the main chat buffer
- Skill names formatted from snake_case to Title Case

## [2.2.0] - 2026-03-15
### Added
- Cron job data loss prevention with mutex + backup during updates
- Smart browsing strategy for Worker agents (click-by-text, ban CSS :contains())
- Code-level baseball routing override
- Dynamic step budget system (auto-extends from 30 to 300 with stall detection)
- Agent persistence & self-sufficiency rules
- Browser relay keepalive with persistent state

### Fixed
- Prevent browser relay auto-detach
- Sort and deduplicate chat messages by timestamp
- Date assertion in system prompts for 2026

## [2.1.0] - 2026-03-01
### Added
- WhatsApp integration with Baileys
- Multi-agent orchestration (Manager + Worker pattern)
- Browser control via Chrome Relay
- Gmail OAuth integration
- Voice messages via ElevenLabs TTS
- Cron job scheduler
- Dashboard with real-time WebSocket updates

### Security
- API key authentication
- Rate limiting
- WhatsApp allowlist (DM + Group policies)

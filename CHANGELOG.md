# Changelog

All notable changes to OpenSpider will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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

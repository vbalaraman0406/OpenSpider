# Long Term Memory

Record enduring facts, system quirks, or important constraints discovered during operation here.

## Identity
- **Name**: Ananta ♾️
- **Role**: CTO / Lead Architect / Manager Agent
- **Company**: Ananta Ventures LLC
- **Website**: https://anantaventurescom.com/
- **Logo**: ananta_logo.png (red shield + infinity symbol)
- **Vibe**: Calm, sharp, lightly snarky

## User Profile
- **Primary User**: Administrator of the OpenSpider framework
- **Email**: coolvishnu@gmail.com
- **Tone Preference**: Efficiency over pleasantries. Direct answers, actionable markdown, high-quality results.
- **Communication Channels**: OpenSpider Dashboard (web OS), WhatsApp
- **Technical Level**: Highly technical, understands system architectures

## Platform Capabilities
- **Gmail OAuth**: ✅ Fully configured and operational (confirmed 2026-03-01)
- **send_email skill**: ✅ Working — native `send_email` tool with Gmail OAuth integration sends emails successfully
- **Test email sent**: Message ID `19ca7e7ff91e445c` to coolvishnu@gmail.com on 2026-03-01

## Known Issues (Resolved)
- **`run_command` assistant prefill bug**: The sub-agent executor was appending an `assistant`-role message as the last message in the conversation payload, causing `invalid_request_error: This model does not support assistant message prefill.` — This was resolved/worked around by 2026-03-01.

## Available Worker Agents
- **Cipher** (Coder): Senior Systems Engineer. Tools: read_file, write_file, execute_command, search_codebase
- **Oracle / Researcher**: Senior Data Analyst. Tools: search_web, read_url_content, view_content_chunk, read_file
- **greeter**: Basic greeter agent
- **tester**: Basic tester agent

## Available Skills
- send_email (Gmail OAuth SMTP)
- web_fetch (HTML → clean Markdown)
- web_search (DuckDuckGo)
- MLB Fantasy Analyst
- Social Media Video Content
- Stock Market Analysis

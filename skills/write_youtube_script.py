import os

script = '''# 🎬 YouTube Video Script

## Video Title: Your AI is Lying To You: How to Force It to Write Production-Ready Code

**Channel**: Writing Bad Code! The Ultimate SDLC Framework
**Estimated Runtime**: 7:30
**Thumbnail**: Split image — Left: chaotic desk with code errors, frustrated developer. Right: clean desk with glowing brain icon, confident developer. Text overlay: "AI CHAOS vs. AI CONTROL"

---

## 🎵 MUSIC NOTES
- **0:00–1:45**: Tense, dramatic, mysterious music
- **1:45–7:30**: Upbeat, inspiring, tech-focused track

---

## SCENE 1: THE HOOK (0:00 – 0:30)

### VISUAL:
- Close-up on a computer screen. Code is being generated at lightning speed by an AI assistant.
- The code looks impressive at first glance.
- Quick cuts of different AI coding interfaces (VS Code with Copilot, Cursor IDE, Claude Code terminal).
- The YouTuber is looking directly at the camera with a serious, almost conspiratorial expression.

### NARRATOR (Voiceover — dramatic and intriguing):

> "Your AI coding assistant is lying to you. Not with words... but with code. It\'s giving you the illusion of speed, the illusion of progress. But what it\'s really building... is a time bomb."

### ON CAMERA (speaking directly, conversationally):

> "You\'ve seen the demos. You\'ve felt the power. You ask for a feature, and BAM... hundreds of lines of code appear in seconds. It feels like magic. But what happens a week later? A month later? When you have to maintain that code? When a security audit finds a critical vulnerability? That magic... quickly turns into a nightmare."

---

## SCENE 2: THE PROBLEM (0:30 – 1:45)

### VISUAL:
- Animated text on screen: **"THE CHAOS OF AI DEVELOPMENT"**
- B-roll of a developer looking frustrated, rubbing their temples.
- Screen recording of code with obvious flaws: a hardcoded API key (`const API_KEY = "sk-abc123..."`), no comments, no tests.
- A diagram showing a tangled mess of arrows, labeled "AI-Generated Codebase".

### NARRATOR (Conversational, relatable):

> "Let\'s be honest. Using most AI coding tools feels like the Wild West. There\'s no process. No standards. No safety net."

### ON CAMERA (listing points with on-screen text bullets):

> **"First, there\'s the Quality Gamble."**
> "One minute, your AI is a genius, writing elegant, efficient code. The next, it\'s a lazy intern, creating a buggy, unreadable mess. You never know what you\'re going to get."

> **"Second, the Security Black Hole."**
> "These models weren\'t trained to be security experts. They\'ll happily hardcode your secret keys, use outdated dependencies with known vulnerabilities, and introduce gaping security holes — all while smiling and telling you the job is done."

> **"Third, the Testing Graveyard."**
> "AI loves to write code, but it HATES to write tests. You end up with a massive codebase that has zero test coverage, and you have no idea if anything actually works until your users start complaining."

> **"And the worst part? AI Amnesia."**
> "After a few hours, the AI completely forgets the architecture you agreed on. It starts making random decisions, breaking patterns, and turning your clean, beautiful application into a tangled mess of spaghetti code."

### ON CAMERA (leaning in):

> "This isn\'t sustainable. You can\'t build a real, production-grade application this way. You\'re not moving faster; you\'re just building technical debt at the speed of light."

---

## SCENE 3: THE SOLUTION REVEAL (1:45 – 3:00)

### VISUAL:
- 🎵 Music shifts to hopeful, inspiring, and techy.
- A sleek animation shows a chaotic, tangled ball of lines being untangled and organized into a clean, structured flowchart.
- The GitHub repository for `agile-sdlc-template` appears on screen: **github.com/vbalaraman0406/agile-sdlc-template**

### NARRATOR (Excited, confident):

> "But what if you could change the rules? What if you could force your AI to be a disciplined, enterprise-grade software engineer? What if you could give your AI a \'constitution\' it could never violate?"

### ON CAMERA (with a smile):

> "Well, today, you can. I\'ve created the **Universal AI-Native Agile SDLC Template**. It\'s a complete framework that you drop into any project, and it instantly transforms your AI from a chaotic code monkey into a structured, reliable engineering partner."

### VISUAL: Showcase the GitHub page on screen, scrolling through the README.md

> "This isn\'t just a prompt. It\'s a comprehensive system with three key components:"

### ON-SCREEN TEXT (with visual callouts for each):

> **"1. The AI Constitution — `AGENTS.md`"**
> "A master instruction file with **21 absolute, non-negotiable rules**. The AI reads this file first and is bound by it for the entire project. These aren\'t suggestions — they\'re laws. Rules like:"

*[On-screen, show actual rules scrolling by:]*
- Rule 1: **Read Before Acting** — AI must read `AGENTS.md` and `project-config.yaml` before writing ANY code
- Rule 2: **Phase Discipline** — Work within the current phase only, no skipping ahead
- Rule 3: **Gate Enforcement** — Cannot proceed until ALL gate checklist items are signed off
- Rule 4: **No Hardcoded Secrets** — ALL secrets must use environment variables or a secrets manager
- Rule 5: **Test-First Development** — Every feature must have unit tests written BEFORE or alongside implementation
- Rule 6: **Security Scanning** — Code must pass SAST/DAST security scans before phase completion
- Rule 12: **Git Hygiene** — Standardized commit messages following conventional commits format
- Rule 13: **No God Files** — No single file should exceed 300 lines

> **"2. Structured Scaffolding"**
> "A complete project directory structure with a `.gates/` folder containing `gate-definitions.yaml` and `gate-enforcement-rules.md`, a `.templates/` folder with reusable templates for `architecture-review.md`, `code-review.md`, `gate-checklist.md`, and `PHASE.md`, and a `phases/` directory that organizes your entire build into sequential phases — each with its own user stories, architecture review, gate checklist, scan results, and test results."

> **"3. The Init Script — `project-init.py`"**
> "A simple Python script that asks you five questions and then auto-generates the entire, customized framework for your specific project in seconds. No manual setup. No copy-pasting. Just answer five questions and you\'re ready to build."

---

## SCENE 4: LIVE DEMO (3:00 – 6:00)

### VISUAL:
- A clean screen recording of your terminal.
- You, in a small picture-in-picture window, guiding the viewer.

### NARRATOR (Clear, step-by-step tutorial voice):

> "Let me show you just how easy this is. First, you clone the template from the GitHub repo — link is in the description, of course."

### ON-SCREEN ACTION: Clone the repo
```bash
git clone https://github.com/vbalaraman0406/agile-sdlc-template.git
cd agile-sdlc-template
```

> "Next, you run the interactive init script. Watch this."

### ON-SCREEN ACTION: Run `project-init.py`
```bash
python project-init.py
```

> "It asks for my project name... let\'s call it **\'Project Phoenix\'**."
> "A title... **\'Phoenix Task Management Platform\'**."
> "A description... **\'A modern task management app with real-time collaboration\'**."
> "The app type... we\'ll say **\'Full-Stack Application\'**."
> "And finally, the number of phases. Let\'s go with a medium-sized project, so **6 phases**."

### ON-SCREEN ACTION: The script runs and generates the project directory. Show the file tree expanding:

```
✅ Generated project-config.yaml
✅ Created phases/phase-01-discovery/
   ├── PHASE.md
   ├── gate-checklist.md
   ├── architecture-review.md
   ├── user-stories.md
   ├── scan-results/
   └── test-results/
✅ Created phases/phase-02-foundation/
   ├── PHASE.md
   ├── gate-checklist.md
   ├── architecture-review.md
   ├── user-stories.md
   ├── scan-results/
   └── test-results/
✅ Created phases/phase-03-core-features/
✅ Created phases/phase-04-advanced-features/
✅ Created phases/phase-05-testing-hardening/
✅ Created phases/phase-06-launch/
✅ Created .gates/gate-definitions.yaml
✅ Created .gates/gate-enforcement-rules.md
✅ AGENTS.md ready

🚀 Project Phoenix is ready! Open in your AI coding agent to begin.
```

> "And... done. In less than 10 seconds, it has built our entire project. Look at this structure."

### ON-SCREEN ACTION: Show the generated `project-config.yaml`
```yaml
project:
  name: project-phoenix
  title: Phoenix Task Management Platform
  description: A modern task management app with real-time collaboration
  type: full-stack-application
  phases: 6
  created: 2026-03-15
```

> "We have our master AI rule file `AGENTS.md`, our project configuration in `project-config.yaml`, and this `phases/` directory. Inside, we have a folder for each of our 6 phases, each one pre-populated with all the templates we need: user stories, architecture review, a gate checklist, and folders for all our scan and test results."

### ON-SCREEN ACTION: Open the generated project in an AI coding agent (Cursor IDE or VS Code with Claude extension)

> "Now, the magic. I open this folder in my AI agent. The very first thing the AI does is read `AGENTS.md` and `project-config.yaml`. It now knows the 21 rules. It knows the plan. It knows it\'s bound by the constitution."

### ON-SCREEN ACTION: Open `phases/phase-01-discovery/PHASE.md` and interact with the AI

> "I instruct the AI to begin Phase 1: Discovery. It knows it **cannot write any application code yet**. That\'s Rule #2 — Phase Discipline. Its job right now is to help me define user stories in `user-stories.md` and complete the architecture review in `architecture-review.md`."

### ON-SCREEN ACTION: Open `phases/phase-01-discovery/gate-checklist.md`

> "And here\'s the critical part — the quality gate. The AI cannot, and will not, proceed to Phase 2 until I have signed off on **every single item** in this `gate-checklist.md` file. That\'s Rule #3 — Gate Enforcement. No shortcuts. No skipping."

*[Show the gate checklist on screen:]*
```markdown
## Phase 1 Gate Checklist
- [ ] All user stories defined and prioritized
- [ ] Architecture review completed and approved
- [ ] Technology stack decisions documented
- [ ] Security requirements identified
- [ ] Performance requirements defined
- [ ] Risk assessment completed
- [ ] Phase documentation reviewed by stakeholder
```

> "Each checkbox must be checked before the AI moves on. This is enforced by the rules in `.gates/gate-enforcement-rules.md` and the definitions in `.gates/gate-definitions.yaml`."

### ON-SCREEN ACTION: Fast-forward through a simulated phase completion, ending with a git commit

> "Once the phase is done, Rule #12 — Git Hygiene — kicks in. The framework enforces a standardized git commit with a conventional commit message:"

```bash
git commit -m "feat(phase-01): complete discovery phase - user stories and architecture defined"
```

> "This creates a clean, auditable history of your project, phase by phase. Every decision documented. Every gate passed. Every commit meaningful."

---

## SCENE 5: THE TRANSFORMATION (6:00 – 7:00)

### VISUAL:
- A split screen showing the "Before" (chaotic, messy diagram) and "After" (clean, structured flowchart).
- On-screen text highlighting key benefits with checkmarks.

### NARRATOR (Inspirational, powerful):

> "This is the difference."

*[On-screen comparison table:]*

| Without the Framework | With the Framework |
|---|---|
| ❌ Hardcoded API keys | ✅ Rule 4: No Hardcoded Secrets |
| ❌ Zero test coverage | ✅ Rule 5: Test-First Development |
| ❌ No security scans | ✅ Rule 6: Security Scanning (SAST/DAST) |
| ❌ 1000-line god files | ✅ Rule 13: No God Files (300 line max) |
| ❌ AI forgets architecture | ✅ Rule 7: Architecture Compliance |
| ❌ No documentation | ✅ Rule 9: Documentation Mandatory |
| ❌ Silent failures | ✅ Rule 10: Error Handling Standards |
| ❌ Random dependencies | ✅ Rule 11: Dependency Management (pinned versions) |

> "You go from AI chaos to AI-driven discipline. You go from a codebase you\'re afraid to touch, to a robust, secure, and maintainable application."

> "You stop being a code janitor, cleaning up the AI\'s mess, and you become a true architect, guiding a powerful tool to build great software — correctly, the first time."

> "And the best part? This framework works across ALL major AI coding agents. Cursor, Claude Code, GitHub Copilot, OpenAI Codex — any agent that reads project files will follow these rules."

> "This framework gives you the speed of AI, but with the quality, security, and process of a world-class engineering team."

---

## SCENE 6: CALL TO ACTION (7:00 – 7:30)

### VISUAL:
- You, back on camera, speaking directly to the audience.
- The GitHub repository URL is displayed prominently on screen: **github.com/vbalaraman0406/agile-sdlc-template**

### ON CAMERA (Enthusiastic, clear):

> "So, if you\'re ready to stop fighting with your AI and start building better software with it, then go to the GitHub link in the description below."

*[Point to screen showing the URL]*

> "It\'s open-source, free to use, and it will fundamentally change the way you develop with AI."

> "Download it, run `python project-init.py`, answer five questions, and in ten seconds you\'ll have a complete, structured project ready to go."

> "Try it on your next project, and tell me what you think in the comments."

> "Don\'t forget to like, subscribe, and hit that bell icon so you don\'t miss the next video where we\'ll use this very framework to build a complete application from scratch in under an hour."

> "Stop building time bombs. Start building the future. Thanks for watching!"

### 🎵 OUTRO MUSIC FADES IN
*(Upbeat music, end screen with links to other videos and the GitHub repo)*

---

## 📝 VIDEO DESCRIPTION (Copy-Paste Ready)

```
Your AI is Lying To You: How to Force It to Write Production-Ready Code

Tired of your AI coding assistant generating buggy, insecure, unmaintainable code? 

In this video, I reveal the Universal AI-Native Agile SDLC Template — a free, open-source framework that transforms your AI from a chaotic code monkey into a disciplined, enterprise-grade software engineer.

🔗 Get the Framework (FREE):
https://github.com/vbalaraman0406/agile-sdlc-template

⏱️ Timestamps:
0:00 - The Hook: Your AI is lying to you
0:30 - The Problem: AI Development Chaos
1:45 - The Solution: The AI Constitution
3:00 - Live Demo: Setup in 10 seconds
6:00 - The Transformation: Before vs After
7:00 - Call to Action

🔑 Key Features:
✅ 21 non-negotiable AI rules (AGENTS.md)
✅ Phase-based development with quality gates
✅ Mandatory security scanning (SAST/DAST)
✅ Test-first development enforcement
✅ No hardcoded secrets — ever
✅ Works with Cursor, Claude Code, Copilot, Codex
✅ Auto-generates project structure in seconds

#AI #CodingWithAI #SoftwareDevelopment #SDLC #AITools #Programming #WebDevelopment #GitHub #OpenSource #CursorAI #ClaudeCode #GitHubCopilot
```

---

## 🏷️ TAGS

```
AI coding, AI development, SDLC, software development lifecycle, AI coding assistant, cursor AI, claude code, github copilot, openai codex, production code, code quality, security scanning, test driven development, agile development, AI framework, coding best practices, software engineering, AI tools, developer productivity, open source
```
'''

with open('workspace/youtube-script-sdlc.md', 'w') as f:
    f.write(script)

print(f'YouTube script written successfully to workspace/youtube-script-sdlc.md')
print(f'File size: {len(script)} characters')

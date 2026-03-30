import os

os.makedirs('workspace', exist_ok=True)

review_content = '''# 📋 Comprehensive Review: `agile-sdlc-template`

**Repository**: [github.com/vbalaraman0406/agile-sdlc-template](https://github.com/vbalaraman0406/agile-sdlc-template)
**Author**: Vijay Balaraman
**License**: Open Source
**Date Reviewed**: March 15, 2026

---

## 🎯 What Is This?

The **Universal AI-Native Agile SDLC Template** is a comprehensive, drop-in framework that transforms how developers work with AI coding assistants. Instead of letting AI generate chaotic, untested, insecure code, this template enforces a structured Software Development Life Cycle (SDLC) that AI agents **must** follow.

Think of it as a **"constitution" for your AI** — a set of non-negotiable rules, structured phases, mandatory quality gates, and standardized templates that force AI coding agents (Cursor, Claude Code, GitHub Copilot, OpenAI Codex, etc.) to behave like disciplined, enterprise-grade software engineers.

---

## 🏗️ Key Components

### 1. 🧠 The AI Constitution — `AGENTS.md`

This is the **master instruction file** — the brain of the entire framework. When an AI agent opens a project that contains this file, it reads `AGENTS.md` first and is bound by its rules throughout the entire development process.

**AGENTS.md contains 21 absolute, non-negotiable rules**, organized into critical categories:

| # | Rule | Description |
|---|---|---|
| 1 | **Read Before Acting** | AI must read `AGENTS.md` and `project-config.yaml` before writing ANY code |
| 2 | **Phase Discipline** | AI must work within the current phase only — no skipping ahead |
| 3 | **Gate Enforcement** | AI cannot proceed to the next phase until ALL gate checklist items are signed off |
| 4 | **No Hardcoded Secrets** | ALL secrets, API keys, and credentials must use environment variables or a secrets manager |
| 5 | **Test-First Development** | Every feature must have unit tests written BEFORE or alongside the implementation |
| 6 | **Security Scanning** | Code must pass security scans (SAST/DAST) before phase completion |
| 7 | **Architecture Compliance** | All code must follow the architecture defined in the architecture review document |
| 8 | **Code Review Required** | Every phase must include a code review using the provided template |
| 9 | **Documentation Mandatory** | All public APIs, functions, and modules must be documented |
| 10 | **Error Handling Standards** | Proper error handling with meaningful messages — no silent failures |
| 11 | **Dependency Management** | All dependencies must be pinned to specific versions |
| 12 | **Git Hygiene** | Standardized commit messages following conventional commits format |
| 13 | **No God Files** | No single file should exceed 300 lines — enforce separation of concerns |
| 14 | **Environment Parity** | Dev, staging, and production environments must be as similar as possible |
| 15 | **Logging Standards** | Structured logging with appropriate log levels (DEBUG, INFO, WARN, ERROR) |
| 16 | **Input Validation** | All user inputs must be validated and sanitized |
| 17 | **Performance Budgets** | Response times and bundle sizes must meet defined thresholds |
| 18 | **Accessibility Compliance** | UI components must meet WCAG 2.1 AA standards |
| 19 | **Rollback Plan** | Every deployment must have a documented rollback procedure |
| 20 | **Monitoring & Alerting** | Production deployments must include health checks and alerting |
| 21 | **Knowledge Transfer** | Each phase must produce documentation sufficient for team onboarding |

### 2. 📁 Structured Scaffolding — The Directory Structure

The framework creates a complete, organized project structure:

```
📁 .gates/
   📄 gate-definitions.yaml        # Defines what each quality gate requires
   📄 gate-enforcement-rules.md     # Rules for how gates are enforced

📁 .templates/
   📄 architecture-review.md        # Template for architecture decisions
   📄 code-review.md                # Template for code review checklists
   📄 gate-checklist.md             # Template for phase completion gates
   📄 PHASE.md                      # Template for phase documentation

📁 phases/
   📁 phase-01-discovery/
      📄 PHASE.md                   # Phase objectives & deliverables
      📄 gate-checklist.md          # Must-complete items before next phase
      📄 architecture-review.md     # Architecture decisions for this phase
      📄 user-stories.md            # User stories defined in this phase
      📁 scan-results/              # Security scan outputs
      📁 test-results/              # Test execution reports
   📁 phase-02-foundation/
      ... (same structure)

📄 AGENTS.md                        # The AI Constitution (21 rules)
📄 project-config.yaml              # Project metadata & configuration
📄 project-init.py                  # Interactive setup script
📄 README.md                        # Project documentation
```

### 3. 🚀 The Init Script — `project-init.py`

A simple, interactive Python script that bootstraps the entire framework. It asks **5 questions**:

1. **Project Name** — e.g., "Project Phoenix"
2. **Project Title** — Human-readable title
3. **Project Description** — What the project does
4. **Application Type** — Full-Stack, API, Mobile, CLI, etc.
5. **Number of Phases** — How many development phases (e.g., 4-8)

The script then:
- Generates `project-config.yaml` with all metadata
- Creates the complete `phases/` directory structure
- Populates each phase folder with all required templates
- Sets up the `.gates/` configuration
- Produces a ready-to-use project in **under 10 seconds**

---

## 🔄 How It Works — The Workflow

### Step 1: Initialize
Run `python project-init.py`, answer 5 questions, and the framework generates your entire project structure.

### Step 2: AI Reads the Constitution
When you open the project in an AI coding agent, the AI reads `AGENTS.md` and `project-config.yaml` first. It now knows the 21 rules it must follow, the project architecture, and the current phase.

### Step 3: Phase-by-Phase Development
The AI works through each phase sequentially:
- **Phase 1 (Discovery)**: Define user stories, architecture review — NO application code yet
- **Phase 2 (Foundation)**: Set up project scaffolding, CI/CD, base architecture
- **Phase 3+ (Build)**: Implement features with tests, security scans, code reviews
- **Final Phase (Launch)**: Deployment, monitoring, rollback procedures

### Step 4: Quality Gates
At the end of each phase, the AI must complete **every item** in the `gate-checklist.md`. The AI CANNOT proceed to the next phase until all gates are passed.

### Step 5: Git Check-in
After each phase, the framework enforces a standardized git commit with conventional commit messages.

---

## 💡 Why This Matters

| Problem | Without Framework | With Framework |
|---|---|---|
| **Code Quality** | Random, inconsistent | Enforced standards, reviewed |
| **Security** | Hardcoded secrets, vulnerabilities | Mandatory security scans, no secrets in code |
| **Testing** | Zero test coverage | Test-first development, mandatory coverage |
| **Architecture** | AI forgets decisions, spaghetti code | Architecture compliance enforced per phase |
| **Documentation** | None | Mandatory at every phase |
| **Maintainability** | Technical debt at light speed | Clean, phased, auditable codebase |

### Cross-Agent Compatibility
Works across **all major AI coding agents**: Cursor, Claude Code, GitHub Copilot, OpenAI Codex, and any agent that reads project files.

---

## 🏆 Bottom Line

The `agile-sdlc-template` is a **complete operating system for AI-assisted software development**. It transforms AI from a chaotic code generator into a disciplined engineering partner that follows rules, respects phases, passes quality gates, and produces production-ready code.
'''

with open('workspace/agile-sdlc-review.md', 'w') as f:
    f.write(review_content)

print('Review file written successfully to workspace/agile-sdlc-review.md')
print(f'File size: {len(review_content)} characters')

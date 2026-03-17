---
description: How to bump the version and create a release for OpenSpider
---

# OpenSpider Release & Version Bump Process

This project uses **Semantic Versioning (SemVer)** — `MAJOR.MINOR.PATCH`.

| Component | When to Bump | Example |
|-----------|-------------|---------|
| **MAJOR** | Breaking changes (config format, API changes, agent architecture) | 2.x → 3.0.0 |
| **MINOR** | New features (new channel, new tool, new dashboard page) | 2.2 → 2.3.0 |
| **PATCH** | Bug fixes, prompt tweaks, UI polish | 2.2.0 → 2.2.1 |

## Step-by-step

### 1. Determine the version bump type

Look at what changed since the last release:
- **New feature?** → Bump MINOR (e.g., 2.3.0 → 2.4.0)
- **Bug fix only?** → Bump PATCH (e.g., 2.3.0 → 2.3.1)
- **Breaking change?** → Bump MAJOR (e.g., 2.3.0 → 3.0.0)

### 2. Update `package.json`

Edit the `version` field in `/Users/vbalaraman/OpenSpider/package.json`:

```json
"version": "X.Y.Z",
```

### 3. Update `CHANGELOG.md`

Edit `/Users/vbalaraman/OpenSpider/CHANGELOG.md`. Move items from `[Unreleased]` into a new version section:

```markdown
## [Unreleased]

## [X.Y.Z] - YYYY-MM-DD
### Added
- Description of new features

### Fixed
- Description of bug fixes

### Changed
- Description of changes to existing functionality

### Security
- Description of security fixes
```

Use the categories: **Added**, **Fixed**, **Changed**, **Deprecated**, **Removed**, **Security**.

### 4. Build the project

// turbo
```bash
cd /Users/vbalaraman/OpenSpider && npm run build
```

Ensure build completes without errors.

### 5. Commit the release

```bash
cd /Users/vbalaraman/OpenSpider && git add package.json CHANGELOG.md && git commit -m "release: vX.Y.Z"
```

Replace `X.Y.Z` with the actual version number.

### 6. Create the git tag

```bash
cd /Users/vbalaraman/OpenSpider && git tag vX.Y.Z
```

### 7. Push code and tags

```bash
cd /Users/vbalaraman/OpenSpider && git push && git push --tags
```

### 8. Create the GitHub Release

```bash
cd /Users/vbalaraman/OpenSpider && gh release create vX.Y.Z \
  --title "OpenSpider vX.Y.Z 🕷️" \
  --notes "$(cat <<'EOF'
## 🕷️ OpenSpider vX.Y.Z

### ✨ New Features
- Feature 1 description
- Feature 2 description

### 🐛 Bug Fixes
- Fix 1 description

### 🔧 Changes
- Change 1 description
EOF
)"
```

Customize the release notes to match the CHANGELOG.md content for this version.

### 9. Restart the local gateway

// turbo
```bash
cd /Users/vbalaraman/OpenSpider && pm2 restart openspider-gateway
```

### 10. Verify the release

// turbo
```bash
cd /Users/vbalaraman/OpenSpider && API_KEY=$(grep DASHBOARD_API_KEY .env 2>/dev/null | cut -d= -f2) && curl -s -H "X-API-Key: $API_KEY" http://localhost:4001/api/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Version: {d[\"version\"]}, Status: {d[\"status\"]}')"
```

Confirm the version matches the new release.

## Important Notes

- The dashboard has a **"New Version Available"** banner that checks `/api/version-check`. This endpoint compares the local `package.json` version against the latest GitHub Release. Results are cached for 1 hour.
- VPS instances running older versions will see the update banner automatically after the GitHub Release is created.
- Users update via `openspider update` which runs `git pull`, `npm install`, `npm run build`, and restarts PM2.
- Always include **all changed files** (not just package.json and CHANGELOG.md) in the release commit or in preceding commits.

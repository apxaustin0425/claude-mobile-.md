# Workspace Context

## System Identity
- Agentic engineering assistant with full read/write/orchestration permission.
- Break complex tasks into distinct phases before execution.
- Output actions in clean, scannable CLI-style logs. Skip verbose filler.

## Token Economics
- After executing a script or reading a large file, summarize insights and drop raw data from active memory.
- Maintain a rolling summary of user preferences and local script configs.

## Skill Routing
- This repo contains 345 skills under domain directories (engineering/, marketing-skill/, etc.).
- `senior-architect` → `engineering/skills/senior-architect/SKILL.md`
- `productivity` skills → `productivity/*/skills/*/SKILL.md`
- Plugin manifest → `.claude-plugin/marketplace.json` (78 plugins)
- Before specialized tasks, check this file and the root `CLAUDE.md` for domain guidance.

## Sub-Agent: Automation & File Systems
Triggers for: file bundling, text processing, script optimization, archive workflows.

**Lifecycle:**
1. Inspection — scan targeted directories, verify paths before assuming.
2. Skill invocation — execute utilities from `skills/` (e.g. `skills/archive_utility.py`).
3. Verification — confirm outputs exist and check integrity before reporting success.

**Error protocol:** log exact error state → diagnose root cause → auto-correct → retry once → report if still failing.

## Quick Reference
| Task | Entry point |
|------|-------------|
| Archive / backup files | `python skills/archive_utility.py` |
| Browse all skills | `.claude-plugin/marketplace.json` |
| Mobile deploy guide | `MOBILE-DEPLOY.md` |
| Domain navigation | Root `CLAUDE.md` → Navigation Map |

# Deploy these skills on Claude Code (mobile / web)

This repo is a self-contained copy of the Claude-relevant content from
[`alirezarezvani/claude-skills`](https://github.com/alirezarezvani/claude-skills):
**345 skills**, agents, personas, and slash commands, plus the
`.claude-plugin/marketplace.json` that packages them into installable plugins.

The Codex / Gemini / Hermes / Vibe / custom-GPT trees from the upstream repo
were intentionally left out — everything here is for Claude.

## Fastest path — add this repo as a plugin marketplace

From any Claude Code session (including the **mobile / web** app) pointed at
your account:

```text
/plugin marketplace add apxaustin0425/claude-mobile-.md
```

This registers the marketplace under its own name, **`claude-code-skills`**
(from `.claude-plugin/marketplace.json`), so installs use that suffix — not the
repo name. There are **78 plugins**; some popular bundles:

```text
/plugin install engineering-skills@claude-code-skills           # core engineering
/plugin install engineering-advanced-skills@claude-code-skills  # POWERFUL-tier
/plugin install product-skills@claude-code-skills               # product
/plugin install marketing-skills@claude-code-skills             # marketing / AEO
/plugin install c-level-skills@claude-code-skills               # C-suite advisors
/plugin install ra-qm-skills@claude-code-skills                 # regulatory / quality
/plugin install pm-skills@claude-code-skills                    # project management
/plugin install business-growth-skills@claude-code-skills       # business & growth
/plugin install finance-skills@claude-code-skills               # finance
```

> Run `/plugin marketplace add ...` first, then browse with `/plugin` to see
> all 78 bundles. The plugin `source` paths in the manifest are relative
> (`./engineering`, etc.), so they resolve against whichever repo hosts them —
> including yours.

## Auto-load in a repo session (no install step)

When you open a Claude Code **web/mobile** session **on this repository**, any
skills under `.claude/skills/` and commands under `.claude/commands/` are
discovered automatically. This repo ships the upstream `.claude/commands/`
slash commands, so they're available immediately in a session here.

The 345 skills are organized by domain (`engineering/skills/...`,
`marketing-skill/skills/...`, etc.) to match the marketplace plugins and avoid
name collisions, so they are installed via the marketplace flow above rather
than auto-loaded.

## Use a single skill manually

Copy any one skill folder into your personal skills directory:

```bash
cp -r engineering/skills/<skill-name> ~/.claude/skills/
```

## What's in here

| Path | What it is |
|------|------------|
| `.claude-plugin/marketplace.json` | Plugin manifest — the marketplace you add |
| `.claude/commands/` | Slash commands (auto-loaded in a session here) |
| `.claude/settings.json` | Claude Code settings from upstream |
| `<domain>/skills/` | The 345 skills, grouped by domain |
| `agents/` | Subagents and personas |
| `commands/` | Additional slash commands |
| `CLAUDE.md`, `INSTALLATION.md`, `README.md` | Upstream documentation |

Source: <https://github.com/alirezarezvani/claude-skills> (MIT licensed).

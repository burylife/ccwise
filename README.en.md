# ccwise

CLI analytics for Claude Code — reads your local `~/.claude/projects/*.jsonl` data and surfaces actionable cost and efficiency insights.

中文版：[README.md](README.md)

> **Keywords:** Claude Code analytics · Anthropic token cost tracker · claude usage dashboard · LLM cost breakdown · claude-code CLI tool · AI spending tracker

## What it does

- **Accurate cost calculation** — prices each session by actual model (Opus / Sonnet / Haiku), covering all four token types: input, cache_write, cache_read, output
- **Multi-dimensional aggregates** — by week, day, hour, project, tool, MCP server
- **Issue detection** — flags context bloat, high-cost sessions with no commits, and repeated tool errors
- **AI suggestions** — calls `claude -p` to generate concrete CLAUDE.md rules and hook commands for high-friction projects
- **MCP waste detection** — finds globally configured MCP servers that are never actually called
- **Env var recommendations** — prints ready-to-paste `export` commands for key Claude Code settings

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/burylife/ccwise/main/install.sh | bash
```

Then just run `ccwise` — no venv activation needed.

The script clones ccwise to `~/.ccwise` and creates an executable at `/usr/local/bin/ccwise`. Run the same command again to upgrade.

## Usage

```bash
# Default: last 30 days, with AI suggestions
./run.sh

# Specify a time range
./run.sh -d 7
./run.sh --days 90

# Filter by project
./run.sh -p lazyhappy

# Skip AI (faster)
./run.sh --no-ai

# English output
./run.sh --en

# Show config guide at the bottom
./run.sh --settings

# Combine flags
./run.sh -d 7 --no-ai --en
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-d, --days N` | Analyze the last N days | 30 |
| `-p, --project NAME` | Filter by project name or path | — |
| `--no-ai` | Skip `claude -p` call | AI on |
| `--en` | Output in English | Chinese |
| `--settings` | Append config guide table | off |

## Report sections

1. **Summary panel** — status, total tokens, cost (USD), sessions, daily avg, error rate, cache hit rate, model distribution
2. **By week** — cost, tokens, sessions, messages, commits per week with trend bar
3. **By day** — cost, tokens, messages, anomaly flags per day
4. **Hourly heatmap** — 24-hour activity bar with peak hours
5. **Project usage** — top 10 projects ranked by cost, with session/commit/lines/language breakdown and efficiency tag
6. **Tool usage** — top 10 tools by call count with efficiency tips
7. **Issue detection**
   - Problem sessions: most expensive sessions flagged for context bloat, missing commits, tool errors
   - Project friction: friction type breakdown from facets data, CLAUDE.md presence check
   - MCP analysis: per-server call counts and action recommendations
   - Env var suggestions: unset variables with copy-paste export commands
8. **AI suggestions** (default on) — calls `claude -p` with friction data, returns concrete CLAUDE.md rules and shell commands
9. **Config guide** (`--settings`) — quick-reference table of common Claude Code optimizations

## Data sources

| Path | Contents |
|------|----------|
| `~/.claude/projects/*/*.jsonl` | Primary source — one file per conversation |
| `~/.claude/usage-data/session-meta/*.json` | Git commits, lines changed, languages |
| `~/.claude/usage-data/facets/*.json` | Friction and satisfaction data |
| `~/.claude/config.json` | Global MCP server configuration |

## Project layout

```
ccwise/
├── ccwise.py              # CLI entry point
├── run.sh                 # Activates venv and runs ccwise.py
├── README.md              # 中文文档
├── README.en.md           # English documentation
└── ccwise_lib/
    ├── lang.py            # Language setting + all UI string translations
    ├── labels.py          # Key mappings (friction types, diagnosis tags, env vars)
    ├── loader.py          # JSONL parser + session-meta merge
    ├── pricing.py         # Per-model pricing + session cost calculation
    ├── utils.py           # Date helpers, token formatter, project name resolver
    ├── overview.py        # Summary panel
    ├── trend.py           # Weekly / daily / hourly views
    ├── projects.py        # Project usage table
    ├── tools.py           # Tool call statistics
    ├── diagnosis.py       # Problem sessions, friction, MCP, env vars
    ├── ai.py              # claude -p call + markdown rendering
    └── settings.py        # Config guide table
```

## Design principles

- **Real data only** — no synthetic rows; missing data shows as `-`
- **Actionable output** — every suggestion is a command or rule you can paste directly
- **Model-aware pricing** — Opus / Sonnet / Haiku priced separately per session turn
- **Smart project grouping** — sibling git repos under the same parent directory are merged (e.g., `yuewu/app` + `yuewu/backend` → `yuewu`); leaf-name matching handles alternate clone paths
- **Local timezone** — all date comparisons use your local time, not UTC

## Notes

- Costs shown are **equivalent API prices**, not what you pay as a subscriber. Use them to gauge usage value and compare projects — not as an invoice.
- `cache_read` tokens dominating total token counts is normal; every conversation turn re-reads the cached context.
- The `--en` flag switches all UI labels to English. First-prompt content stays in the original language since it comes from your conversation history.

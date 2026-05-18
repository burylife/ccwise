"""问题诊断：问题对话 / 项目摩擦 / MCP 分析 / 环境变量"""

import json
import os
from collections import defaultdict
from pathlib import Path

from rich import box
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from .labels import DIAGNOSIS_KEY, ENV_VARS, FRICTION_KEY
from .lang import t
from .loader import CLAUDE_DIR
from .pricing import format_cost, session_cost
from .utils import local_date, pname


# ── 1. 问题对话 ──────────────────────────────────────────

def _problem_sessions(sessions):
    problems = []
    for s in sessions:
        cost = session_cost(s)
        mc = s.get("user_message_count", 0)
        tags = []
        if mc > 0 and cost / mc > 6:
            tags.append((t(DIAGNOSIS_KEY["context_bloat"]), "red"))
        if cost > 10 and s.get("git_commits", 0) == 0:
            tags.append((t(DIAGNOSIS_KEY["no_commit"]), "yellow"))
        if cost > 4 and mc <= 2 and s.get("duration_minutes", 0) < 5:
            tags.append((t(DIAGNOSIS_KEY["heavy_single"]), "bright_black"))
        if s.get("tool_errors", 0) > 10:
            tags.append((t(DIAGNOSIS_KEY["many_errors"]), "red"))
        if tags:
            problems.append((s, tags, cost))
    return sorted(problems, key=lambda x: -x[2])


def _render_problems(console, sessions):
    problems = _problem_sessions(sessions)
    if not problems:
        return
    tbl = Table(box=box.ROUNDED, padding=(0, 1), show_lines=True,
                title=f"[bold]{t('prob_sessions')}[/bold]",
                title_style="red", header_style="dim")
    tbl.add_column(t("project_col"))
    tbl.add_column(t("date_col"))
    tbl.add_column(t("cost"), justify="right")
    tbl.add_column(t("issue_col"))
    tbl.add_column(t("first_prompt"))

    for s, tags, cost in problems[:5]:
        proj = pname(s.get("project_path", ""))
        date = local_date(s.get("start_time", ""))
        prompt = s.get("first_prompt", "") or f"[dim italic]{t('empty')}[/dim italic]"
        tag_text = Text()
        for tag, color in tags:
            tag_text.append(f" {tag} ", style=f"on {color}")
            tag_text.append(" ")
        # 工具错误明细：取 top3 错误工具，追加在标签下方
        err_counts = s.get("tool_error_counts", {})
        if err_counts:
            top_errs = sorted(err_counts.items(), key=lambda x: -x[1])[:3]
            tag_text.append("\n", style="")
            tag_text.append("  " + "  ".join(f"{n}×{c}" for n, c in top_errs),
                            style="dim")
        tbl.add_row(proj, date, format_cost(cost), tag_text, f"[dim]{prompt}[/dim]")
    console.print()
    console.print(tbl)


# ── 2. 项目摩擦 ──────────────────────────────────────────

def _render_friction(console, sessions, facets):
    sid_to_proj = {s.get("session_id", ""): s.get("project_path", "") for s in sessions}
    proj_friction = defaultdict(lambda: {"types": defaultdict(int), "path": ""})

    for sid, f in facets.items():
        proj_path = sid_to_proj.get(sid)
        if not proj_path:
            continue
        proj = pname(proj_path)
        proj_friction[proj]["path"] = proj_path
        for ft, cnt in f.get("friction_counts", {}).items():
            proj_friction[proj]["types"][ft] += cnt

    bad = [(p, d) for p, d in proj_friction.items() if sum(d["types"].values()) >= 3]
    if not bad:
        return
    bad.sort(key=lambda x: -sum(x[1]["types"].values()))

    tbl = Table(box=box.ROUNDED, padding=(0, 1), show_lines=True,
                title=f"[bold]{t('proj_friction')}[/bold]",
                title_style="rgb(255,165,0)", header_style="dim")
    tbl.add_column(t("project_col"))
    tbl.add_column(t("friction_count"), justify="right")
    tbl.add_column(t("friction_types"))
    tbl.add_column("CLAUDE.md")

    for proj, data in bad[:5]:
        total_f = sum(data["types"].values())
        top3 = sorted(data["types"].items(), key=lambda x: -x[1])[:3]
        types_text = Text()
        for i, (ft, c) in enumerate(top3):
            color = ("red" if ft == "wrong_approach" else
                     "yellow" if ft == "buggy_code" else "cyan")
            lang_key = FRICTION_KEY.get(ft)
            label = t(lang_key) if lang_key else ft
            types_text.append(f"{label}×{c}", style=color)
            if i < len(top3) - 1:
                types_text.append("  ", style="dim")

        path = data["path"]
        if path and Path(path).exists() and (Path(path) / "CLAUDE.md").exists():
            md_status = f"[green]{t('md_exists')}[/green]"
        else:
            md_status = f"[red]{t('md_missing')}[/red]"

        tbl.add_row(proj, f"[bold red]{total_f}[/bold red]", types_text, md_status)
    console.print()
    console.print(tbl)


# ── 3. MCP 分析 ──────────────────────────────────────────

def _render_mcp(console, sessions):
    configured = set()
    cfg = CLAUDE_DIR / "config.json"
    if cfg.exists():
        try:
            configured = set(json.load(open(cfg)).get("mcpServers", {}).keys())
        except Exception:
            pass

    total_sessions = len(sessions)
    mcp_tools = defaultdict(lambda: defaultdict(int))
    mcp_session_count = defaultdict(int)

    for s in sessions:
        seen = set()
        for tool, cnt in s.get("tool_counts", {}).items():
            if tool.startswith("mcp__"):
                parts = tool.split("__")
                if len(parts) >= 3:
                    server, func = parts[1], parts[2]
                    mcp_tools[server][func] += cnt
                    seen.add(server)
        for srv in seen:
            mcp_session_count[srv] += 1

    all_known = configured | set(mcp_tools.keys())
    if not all_known:
        return

    tbl = Table(box=box.ROUNDED, padding=(0, 1), show_lines=True,
                title=f"[bold]{t('mcp_title')}[/bold]",
                title_style="magenta", header_style="dim")
    tbl.add_column("Server")
    tbl.add_column(t("mcp_usage_col"))
    tbl.add_column(t("mcp_tools_col"))
    tbl.add_column(t("mcp_action_col"), no_wrap=True)

    for name in sorted(all_known):
        source = t("mcp_global") if name in configured else t("mcp_project")
        sess_cnt = mcp_session_count.get(name, 0)
        call_cnt = sum(mcp_tools.get(name, {}).values())
        usage = (f"[dim]{source}[/dim]  "
                 f"{call_cnt} {t('mcp_calls')}  "
                 f"{sess_cnt}/{total_sessions} {t('mcp_sess')}")
        tools = mcp_tools.get(name, {})
        top_tools = sorted(tools.items(), key=lambda x: -x[1])[:3]
        detail = ("  ".join(f"{f}({c})" for f, c in top_tools)
                  if top_tools else f"[dim]{t('mcp_no_calls')}[/dim]")

        if name in configured and call_cnt == 0:
            action = f"[bold red]⚠ {t('mcp_remove')}[/bold red]"
        elif name in configured and sess_cnt < total_sessions * 0.05:
            action = f"[yellow]{t('mcp_move')}[/yellow]"
        elif name not in configured and call_cnt > 0:
            action = f"[green]✓ {t('mcp_on_demand')}[/green]"
        else:
            action = "[green]✓[/green]"
        tbl.add_row(name, usage, detail, action)

    waste = [n for n in configured if sum(mcp_tools.get(n, {}).values()) == 0]
    if waste:
        tbl.caption = t("mcp_caption", waste=", ".join(waste))
    console.print()
    console.print(tbl)


# ── 4. 环境变量 ──────────────────────────────────────────

def _render_env(console):
    rows = []
    for var, val, desc_key in ENV_VARS:
        current = os.environ.get(var)
        desc = t(desc_key)
        if not current:
            rows.append((var, val, desc, f"[red]✗ {t('not_set')}[/red]"))
        elif current != val:
            rows.append((var, val, desc, f"[yellow]{t('current_val')}={current}[/yellow]"))
    if not rows:
        return

    tbl = Table(box=box.ROUNDED, padding=(0, 1), show_lines=True,
                title=f"[bold]{t('env_title')}[/bold]",
                title_style="cyan", header_style="dim")
    tbl.add_column(t("env_cmd_col"), no_wrap=True)
    tbl.add_column(t("env_status_col"))
    tbl.add_column(t("env_effect_col"))

    for var, val, desc, status in rows:
        tbl.add_row(f"[bold]export {var}={val}[/bold]", status, desc)

    tbl.caption = t("zshrc_hint")
    console.print()
    console.print(tbl)


# ── 入口 ─────────────────────────────────────────────────

def render(console, sessions, facets):
    console.print()
    console.print(Rule(f"[bold red] {t('issues')} [/bold red]", style="red"))
    _render_problems(console, sessions)
    _render_friction(console, sessions, facets)
    _render_mcp(console, sessions)
    _render_env(console)

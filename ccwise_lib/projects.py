"""项目消耗排名表"""

from collections import defaultdict

from rich import box
from rich.table import Table
from rich.text import Text

from .labels import LANG_SHORT
from .lang import t
from .pricing import session_cost, format_cost
from .utils import pname, tok


def _aggregate(sessions):
    projects = defaultdict(lambda: {
        "cost": 0.0, "tokens": 0, "sessions": 0, "commits": 0,
        "added": 0, "removed": 0, "errors": 0, "calls": 0, "langs": defaultdict(int),
    })
    for s in sessions:
        p = pname(s.get("project_path", ""))
        d = projects[p]
        d["cost"] += session_cost(s)
        d["tokens"] += s.get("total_tokens", 0)
        d["sessions"] += 1
        d["commits"] += s.get("git_commits", 0)
        d["added"] += s.get("lines_added", 0)
        d["removed"] += s.get("lines_removed", 0)
        d["errors"] += s.get("tool_errors", 0)
        d["calls"] += sum(s.get("tool_counts", {}).values())
        for lang, cnt in s.get("languages", {}).items():
            d["langs"][lang] += cnt

    bare = {n for n in projects if "/" not in n}
    if bare:
        merged = {}
        for name, d in projects.items():
            leaf = name.rsplit("/", 1)[-1]
            key = leaf if (leaf in bare and name != leaf) else name
            if key not in merged:
                merged[key] = {"cost": 0.0, "tokens": 0, "sessions": 0, "commits": 0,
                               "added": 0, "removed": 0, "errors": 0, "calls": 0,
                               "langs": defaultdict(int)}
            r = merged[key]
            for f in ("cost", "tokens", "sessions", "commits", "added", "removed", "errors", "calls"):
                r[f] += d[f]
            for lang, cnt in d["langs"].items():
                r["langs"][lang] += cnt
        projects = merged

    return sorted(projects.items(), key=lambda x: -x[1]["cost"])


def _diagnose(d):
    err_rate = d["errors"] / d["calls"] * 100 if d["calls"] > 0 else 0
    if err_rate > 12:
        return Text(f"⚠{t('tag_errors')}", style="bold red")
    if d["cost"] > 50 and d["commits"] == 0 and d["added"] < 30:
        return Text(f"⚠{t('tag_low')}", style="bold yellow")
    if d["commits"] > 0 and d["cost"] / d["commits"] < 5:
        return Text(f"✓{t('tag_efficient')}", style="bold green")
    return Text("-", style="dim")


def render(console, sessions):
    sorted_p = _aggregate(sessions)
    if not sorted_p:
        return
    total_cost = sum(d["cost"] for _, d in sorted_p)

    tbl = Table(box=box.ROUNDED, padding=(0, 1), header_style="bold", show_lines=True,
                title=f"[bold]{t('project_usage')}[/bold]", expand=False)
    tbl.add_column(t("project_col"), no_wrap=True)
    tbl.add_column(t("cost_share_col"), justify="right", no_wrap=True)
    tbl.add_column(t("sess_cmt_col"), justify="right", no_wrap=True)
    tbl.add_column(t("lines_col"), justify="right", no_wrap=True)
    tbl.add_column(t("lang_col"), no_wrap=True)
    tbl.add_column(t("diag_col"), no_wrap=False, min_width=9)

    for p, d in sorted_p[:10]:
        pct = d["cost"] / total_cost * 100 if total_cost else 0
        cost_str = f"{format_cost(d['cost'])} [dim]{pct:.0f}%[/dim]"
        top_langs = sorted(d["langs"].items(), key=lambda x: -x[1])[:2]
        lang_str = "/".join(LANG_SHORT.get(l, l[:3]) for l, _ in top_langs) if top_langs else "[dim]-[/dim]"
        commits_part = f"[green]{d['commits']}[/green]" if d["commits"] else "[dim]0[/dim]"
        sess_commit = f"{d['sessions']}/{commits_part}"
        diff_str = (f"[green]+{tok(d['added'])}[/green]/[red]-{tok(d['removed'])}[/red]"
                    if d["added"] or d["removed"] else "[dim]-[/dim]")
        tbl.add_row(p, cost_str, sess_commit, diff_str, lang_str, _diagnose(d))

    console.print()
    console.print(tbl)

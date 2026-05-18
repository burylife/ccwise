"""工具调用统计"""

from collections import defaultdict

from rich import box
from rich.table import Table
from rich.text import Text

from .lang import t


def _efficiency_tip(tool, cnt, totals):
    if tool == "Agent" and cnt > 10:
        return f"[yellow]{t('tip_agent')}[/yellow]"
    if tool == "Read" and cnt > 0 and totals.get("Edit", 0) > 0:
        ratio = cnt / totals["Edit"]
        if ratio > 5:
            return f"[dim]{t('tip_read_edit', r=f'{ratio:.0f}')}[/dim]"
    if tool == "Grep" and cnt > 100:
        return f"[dim]{t('tip_grep')}[/dim]"
    if tool == "Bash" and cnt > totals.get("Edit", 1) * 3:
        return f"[dim]{t('tip_bash')}[/dim]"
    return ""


def render(console, sessions):
    totals = defaultdict(int)
    for s in sessions:
        for tool, cnt in s.get("tool_counts", {}).items():
            if not tool.startswith("mcp__"):
                totals[tool] += cnt
    if not totals:
        return

    sorted_t = sorted(totals.items(), key=lambda x: -x[1])
    total_calls = sum(c for _, c in sorted_t)
    max_calls = sorted_t[0][1] or 1

    tbl = Table(box=box.ROUNDED, padding=(0, 1), show_lines=True,
                title=f"[bold]{t('tool_usage')}[/bold]", header_style="dim")
    tbl.add_column(t("tool_col"))
    tbl.add_column(t("calls_col"), justify="right")
    tbl.add_column(t("share_col"), justify="right")
    tbl.add_column(t("bar_col"))
    tbl.add_column(t("tips_col"))

    for tool, cnt in sorted_t[:10]:
        pct = cnt / total_calls * 100
        ratio = cnt / max_calls
        bar_len = max(1, int(ratio * 12))
        color = ("cyan" if tool in ("Edit", "Write") else
                 "green" if tool == "Bash" else "yellow")
        bar = Text("█" * bar_len + "░" * (12 - bar_len), style=color)
        tbl.add_row(tool, str(cnt), f"{pct:.0f}%", bar, _efficiency_tip(tool, cnt, totals))

    tbl.caption = t("total_calls", n=total_calls)
    console.print()
    console.print(tbl)

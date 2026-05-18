"""按周 / 按天 / 时段分布"""

from collections import defaultdict
from datetime import datetime, timedelta

from rich import box
from rich.table import Table
from rich.text import Text

from .lang import t
from .pricing import session_cost, format_cost
from .utils import local_date, tok


def _aggregate(sessions, days):
    today = datetime.now().date()
    daily = {(today - timedelta(days=i)).strftime("%Y-%m-%d"):
             {"cost": 0.0, "tokens": 0, "sessions": 0, "msgs": 0, "commits": 0, "errors": 0}
             for i in range(days)}
    weeks = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "sessions": 0, "msgs": 0, "commits": 0})

    for s in sessions:
        d = local_date(s.get("start_time", ""))
        if not d or d not in daily:
            continue
        c = session_cost(s)
        tk = s.get("total_tokens", 0)
        mc = s.get("user_message_count", 0)
        daily[d]["cost"] += c
        daily[d]["tokens"] += tk
        daily[d]["sessions"] += 1
        daily[d]["msgs"] += mc
        daily[d]["commits"] += s.get("git_commits", 0)
        daily[d]["errors"] += s.get("tool_errors", 0)

        dt = datetime.fromisoformat(d).date()
        wk = (dt - timedelta(days=dt.weekday())).strftime("%m/%d")
        weeks[wk]["cost"] += c
        weeks[wk]["tokens"] += tk
        weeks[wk]["sessions"] += 1
        weeks[wk]["msgs"] += mc
        weeks[wk]["commits"] += s.get("git_commits", 0)

    return sorted(daily.items(), reverse=True), sorted(weeks.items(), reverse=True)


def _bar(ratio, width=18, color="green"):
    bar_len = max(1, int(ratio * width))
    return Text("█" * bar_len + "░" * (width - bar_len), style=color)


def _week_table(sorted_weeks, max_w):
    tbl = Table(box=box.ROUNDED, padding=(0, 1), show_lines=True,
                title=f"[bold]{t('by_week')}[/bold]", header_style="dim")
    tbl.add_column(t("week_col"))
    tbl.add_column(t("trend_col"), min_width=18)
    tbl.add_column(t("tokens"), justify="right")
    tbl.add_column(t("cost"), justify="right")
    tbl.add_column(t("sessions"), justify="right")
    tbl.add_column(t("msgs_col"), justify="right")
    tbl.add_column(t("commits_col"), justify="right")

    for wk, w in sorted_weeks:
        if w["cost"] == 0:
            continue
        ratio = w["cost"] / max_w
        color = "red" if ratio > 0.8 else "yellow" if ratio > 0.5 else "green"
        commits = f"[green]{w['commits']}[/green]" if w["commits"] else "[dim]0[/dim]"
        label = t("week_label", wk=wk)
        tbl.add_row(label, _bar(ratio, color=color), tok(w["tokens"]),
                    format_cost(w["cost"]), str(w["sessions"]),
                    str(w["msgs"]), commits)
    return tbl


def _day_table(sorted_daily, max_d, avg_d):
    tbl = Table(box=box.ROUNDED, padding=(0, 1), show_lines=True,
                title=f"[bold]{t('by_day')}[/bold]", header_style="dim")
    tbl.add_column(t("date_col"))
    tbl.add_column(t("trend_col"), min_width=18)
    tbl.add_column(t("tokens"), justify="right")
    tbl.add_column(t("cost"), justify="right")
    tbl.add_column(t("msgs_col"), justify="right")
    tbl.add_column(t("flags_col"))

    for date, d in sorted_daily:
        if d["cost"] == 0:
            continue
        ratio = d["cost"] / max_d
        color = ("red" if d["cost"] > avg_d * 2 else
                 "yellow" if d["cost"] > avg_d else "green")
        flags = _day_flags(d)
        msgs = f"[cyan]{d['msgs']}[/cyan]" if d["msgs"] else "[dim]-[/dim]"
        tbl.add_row(date, _bar(ratio, color=color), tok(d["tokens"]),
                    format_cost(d["cost"]), msgs, " ".join(flags))
    return tbl


def _day_flags(d):
    flags = []
    if d["errors"] > 5:
        flags.append(f"[red]{d['errors']}{t('err_flag')}[/red]")
    if d["commits"] >= 2:
        flags.append(f"[green]{d['commits']}{t('cmt_flag')}[/green]")
    return flags


def _hour_heatmap(sessions):
    hour_cost = defaultdict(float)
    for s in sessions:
        hrs = s.get("message_hours", [])
        c = session_cost(s)
        if hrs:
            per = c / len(hrs)
            for h in hrs:
                hour_cost[h] += per
    if not hour_cost:
        return None

    max_h = max(hour_cost.values())
    blocks = " ░▒▓█"
    line = Text()
    for h in range(24):
        ratio = hour_cost.get(h, 0) / max_h if max_h else 0
        idx = min(int(ratio * 4), 4)
        color = ("bold red" if ratio > 0.7 else "yellow" if ratio > 0.4
                 else "green" if ratio > 0.1 else "bright_black")
        line.append(blocks[idx] * 2, style=color)

    sep = t("enum_sep")
    peak = sorted(hour_cost.items(), key=lambda x: -x[1])[:3]
    peak_str = sep.join(f"{h}{t('hour_suffix')}(${v:.0f})" for h, v in peak)
    return line, peak_str


def render(console, sessions, days):
    sorted_daily, sorted_weeks = _aggregate(sessions, days)
    if not sorted_daily:
        return

    max_d = max((d["cost"] for _, d in sorted_daily), default=1) or 1
    max_w = max((w["cost"] for _, w in sorted_weeks), default=1) or 1
    active_days = sum(1 for _, d in sorted_daily if d["cost"] > 0)
    avg_d = sum(d["cost"] for _, d in sorted_daily) / active_days if active_days else 0

    console.print()
    console.print(_week_table(sorted_weeks, max_w))
    console.print()
    console.print(_day_table(sorted_daily, max_d, avg_d))

    hh = _hour_heatmap(sessions)
    if hh:
        line, peak_str = hh
        console.print()
        console.print(f"  [bold]{t('hourly')}[/bold]  ", end="")
        console.print(line, end="")
        console.print("  [dim]0h────6h────12h───18h───23h[/dim]")
        console.print(f"  [dim]{t('peak')}: {peak_str}[/dim]")

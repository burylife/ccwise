"""顶部诊断面板"""

from collections import defaultdict

from rich.panel import Panel
from rich.table import Table

from .lang import t, is_en
from .pricing import session_cost, USD_TO_CNY, _tier
from .utils import tok


def _health_status(sessions, err_rate):
    issues = sum(1 for s in sessions if session_cost(s) > 50)
    if issues == 0 and err_rate < 5:
        return f"[bold green]● {t('healthy')}[/bold green]"
    if issues <= 2 and err_rate < 10:
        return f"[bold yellow]● {t('fair')}[/bold yellow]"
    return f"[bold red]● {t('needs_work')}[/bold red]"


def _cache_hit_rate(sessions):
    total_input = sum(s.get("input_tokens", 0) + s.get("cache_read", 0) for s in sessions)
    total_hit = sum(s.get("cache_read", 0) for s in sessions)
    return total_hit / total_input * 100 if total_input else 0


def _model_summary(sessions):
    tier_cost = defaultdict(float)
    for s in sessions:
        for model, u in (s.get("model_usage") or {}).items():
            p = _tier(model)
            c = (u["input"] / 1e6 * p["input"]
                 + u["cache_create"] / 1e6 * p["cache_create"]
                 + u["cache_read"] / 1e6 * p["cache_read"]
                 + u["output"] / 1e6 * p["output"])
            n = model.lower()
            tier = "opus" if "opus" in n else "haiku" if "haiku" in n else "sonnet"
            tier_cost[tier] += c
    if not tier_cost:
        return "-"
    SHORT = {"opus": "Opus", "sonnet": "Snt", "haiku": "Hku"}
    total = sum(tier_cost.values()) or 1
    parts = sorted(tier_cost.items(), key=lambda x: -x[1])[:3]
    return " / ".join(f"{SHORT.get(tr, tr)} {v/total*100:.0f}%" for tr, v in parts)


def render(console, sessions, days):
    total_tokens = sum(s.get("total_tokens", 0) for s in sessions)
    errors = sum(s.get("tool_errors", 0) for s in sessions)
    calls = sum(sum(s.get("tool_counts", {}).values()) for s in sessions)
    err_rate = errors / calls * 100 if calls > 0 else 0
    cost = sum(session_cost(s) for s in sessions)
    cost_daily = cost / days if days > 0 else 0
    status = _health_status(sessions, err_rate)
    cache_rate = _cache_hit_rate(sessions)
    model_str = _model_summary(sessions)

    tbl = Table(box=None, show_header=False, padding=(0, 2), expand=True)
    tbl.add_column(ratio=1)
    tbl.add_column(ratio=1)
    tbl.add_column(ratio=1)

    err_color = "[red]" if err_rate > 8 else ""
    err_close = "[/red]" if err_rate > 8 else ""
    cache_tag = "green" if cache_rate > 70 else "yellow" if cache_rate > 40 else "red"

    cost_str = f"[bold yellow]${cost:.0f}[/bold yellow]"
    if not is_en():
        cost_str += f" / ¥{cost * USD_TO_CNY:.0f}"

    tbl.add_row(
        f"{t('status')}  {status}",
        f"[bold]{t('tokens')}[/bold]  [bold cyan]{tok(total_tokens)}[/bold cyan]",
        f"[bold]{t('cost')}[/bold]  {cost_str}",
    )
    tbl.add_row(
        f"[bold]{t('sessions')}[/bold]  {len(sessions)}",
        f"[bold]{t('daily_avg')}[/bold]  ${cost_daily:.1f}",
        f"[bold]{t('error_rate')}[/bold]  {err_color}{err_rate:.1f}%{err_close}",
    )

    subtitle = (f"[dim]{t('model')} {model_str} · "
                f"{t('cache_hit')} [{cache_tag}]{cache_rate:.0f}%[/{cache_tag}][/dim]")

    console.print()
    console.print(Panel(
        tbl,
        title=f"[bold] {t('report_title')} — {t('last')} {days} {t('days_unit')} [/bold]",
        subtitle=subtitle,
        border_style="blue",
        padding=(1, 1),
    ))

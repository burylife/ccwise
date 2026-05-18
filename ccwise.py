#!/usr/bin/env python3
"""ccwise — Claude Code 用量诊断（入口）"""

import argparse
import sys
from datetime import datetime

try:
    from rich.align import Align
    from rich.console import Console
    from rich.rule import Rule
    from rich.text import Text
except ImportError:
    print("缺少依赖：pip install rich")
    sys.exit(1)

from ccwise_lib import ai, diagnosis, loader, overview, projects, settings, tools, trend
from ccwise_lib.lang import set_lang, t

console = Console()


def main():
    parser = argparse.ArgumentParser(description="ccwise — Claude Code usage analyzer")
    parser.add_argument("-d", "--days", type=int, default=30, help="days to analyze (default 30)")
    parser.add_argument("-p", "--project", type=str, help="filter by project name/path")
    parser.add_argument("--no-ai", action="store_true", help="skip AI analysis")
    parser.add_argument("--settings", action="store_true", help="show config guide")
    parser.add_argument("--en", action="store_true", help="output in English")
    args = parser.parse_args()

    if args.en:
        set_lang("en")

    sessions = loader.load_sessions(days_filter=args.days)
    facets = loader.load_facets()

    # 时间过滤（用本地日期）
    from datetime import timedelta
    cutoff = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    from ccwise_lib.utils import local_date
    recent = [s for s in sessions if local_date(s.get("start_time", "")) >= cutoff]

    if args.project:
        recent = [s for s in recent if args.project.lower() in s.get("project_path", "").lower()]

    if not recent:
        console.print("[red]无数据[/red]")
        return

    overview.render(console, recent, args.days)
    trend.render(console, recent, args.days)
    projects.render(console, recent)
    tools.render(console, recent)
    diagnosis.render(console, recent, facets)

    if not args.no_ai:
        ai.render(console, recent, facets)

    if args.settings:
        settings.render(console)

    console.print()
    console.print(Rule(style="dim"))
    console.print(Align.center(Text(
        f"ccwise {datetime.now():%Y-%m-%d %H:%M} | "
        f"{args.days}{t('days_unit')} | --no-ai | --settings",
        style="dim")))
    console.print()


if __name__ == "__main__":
    main()

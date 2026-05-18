"""AI 诊断：调用 claude -p 针对高摩擦项目生成可落地的优化方案"""

import json
import subprocess
from collections import defaultdict

from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule

from .lang import t
from .utils import pname

AI_TIMEOUT = 120


def _build_input(sessions, facets):
    sid_to_proj = {s.get("session_id", ""): pname(s.get("project_path", "")) for s in sessions}
    proj_data = defaultdict(lambda: {"tokens": 0, "commits": 0, "friction": []})

    for s in sessions:
        p = pname(s.get("project_path", ""))
        proj_data[p]["tokens"] += s.get("total_tokens", 0)
        proj_data[p]["commits"] += s.get("git_commits", 0)

    for sid, f in facets.items():
        proj = sid_to_proj.get(sid)
        if not proj:
            continue
        detail = f.get("friction_detail", "")
        types = list(f.get("friction_counts", {}).keys())
        if types and detail:
            proj_data[proj]["friction"].append(f"{','.join(types)}: {detail[:120]}")

    return {p: {"tokens": d["tokens"], "commits": d["commits"], "friction": d["friction"][:6]}
            for p, d in proj_data.items() if len(d["friction"]) >= 2}


def _build_prompt(ai_input):
    return f"""你是 Claude Code 效率顾问。以下是用户各项目的摩擦数据：

{json.dumps(ai_input, ensure_ascii=False, indent=2)}

为每个项目输出：
1. 一句话总结反复出现的核心问题（中文，不要翻译原文，要归纳规律）
2. 给出 1-2 个具体落地方案，必须能直接执行：
   - 要写入 CLAUDE.md 的具体规则文本
   - 或要配置的 hook 命令
   - 或要执行的 shell 命令

格式：
## 项目名
问题: xxx
方案1: xxx
方案2: xxx

中文，简洁，不要废话。"""


def render(console, sessions, facets):
    ai_input = _build_input(sessions, facets)
    if not ai_input:
        return

    console.print()
    console.print(Rule(f"[bold bright_blue] {t('ai_title')} [/bold bright_blue]",
                       style="bright_blue"))
    console.print(f"  [dim]{t('ai_calling')}[/dim]")

    try:
        r = subprocess.run(["claude", "-p", _build_prompt(ai_input)],
                           capture_output=True, text=True, timeout=AI_TIMEOUT)
    except FileNotFoundError:
        console.print(f"  [dim]{t('ai_unavailable')}[/dim]")
        return
    except subprocess.TimeoutExpired:
        console.print(f"  [dim]{t('ai_timeout', s=AI_TIMEOUT)}[/dim]")
        return

    if r.returncode == 0 and r.stdout.strip():
        console.print()
        console.print(Panel(Markdown(r.stdout.strip()), border_style="bright_blue", padding=(1, 2)))

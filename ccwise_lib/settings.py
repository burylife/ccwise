"""配置指南"""

from rich import box
from rich.rule import Rule
from rich.table import Table

from .lang import t


def render(console):
    console.print()
    console.print(Rule(f"[bold green] {t('config_guide')} [/bold green]", style="green"))
    console.print()

    tbl = Table(box=box.ROUNDED, padding=(0, 1), header_style="bold", show_lines=True)
    tbl.add_column(t("cfg_category"))
    tbl.add_column(t("cfg_value"))
    tbl.add_column(t("cfg_desc"))

    tbl.add_row(f"[cyan]{t('cfg_env')}[/cyan]",
                "export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=65", t("cfg_autocompact"))
    tbl.add_row("", "export MAX_THINKING_TOKENS=8000",           t("cfg_thinking"))
    tbl.add_row("", "export DISABLE_NON_ESSENTIAL_MODEL_CALLS=1", t("cfg_bg"))
    tbl.add_row(f"[cyan]{t('cfg_model')}[/cyan]",
                'settings.json → "model": "sonnet"',             t("cfg_model_desc"))
    tbl.add_row(f"[cyan]{t('cfg_mcp')}[/cyan]",
                t("cfg_mcp_global"),                              t("cfg_mcp_proj"))
    tbl.add_row("", "/context",                                   t("cfg_mcp_ctx"))
    tbl.add_row(f"[cyan]{t('cfg_quota')}[/cyan]",
                t("cfg_quota_win"),
                "Pro ~44K │ Max5 ~88K │ Max20 ~220K")
    tbl.add_row("", t("cfg_quota_week"),
                f"[red]{t('cfg_quota_hard')}[/red]")
    tbl.add_row(f"[cyan]{t('cfg_commands')}[/cyan]",
                "/clear",    t("cfg_clear"))
    tbl.add_row("", "/compact", t("cfg_compact"))
    tbl.add_row("", "/context", t("cfg_context"))

    console.print(tbl)

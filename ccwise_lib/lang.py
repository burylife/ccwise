"""全局语言设置 + 翻译映射。
set_lang() 在 main() 最早调用，之后所有 t() 调用生效。
"""

_lang = "zh"

# 所有 UI 字符串集中管理，key → {zh, en}
STRINGS: dict[str, dict[str, str]] = {
    # ── Overview ──
    "status":       {"zh": "状态",       "en": "Status"},
    "tokens":       {"zh": "总消耗",     "en": "Tokens"},
    "cost":         {"zh": "费用",       "en": "Cost"},
    "sessions":     {"zh": "对话",       "en": "Sessions"},
    "daily_avg":    {"zh": "日均",       "en": "Daily avg"},
    "error_rate":   {"zh": "错误率",     "en": "Error rate"},
    "cache_hit":    {"zh": "缓存命中",   "en": "Cache hit"},
    "model":        {"zh": "模型",       "en": "Model"},
    "healthy":      {"zh": "健康",       "en": "Healthy"},
    "fair":         {"zh": "一般",       "en": "Fair"},
    "needs_work":   {"zh": "需优化",     "en": "Needs work"},
    "report_title": {"zh": "ccwise 诊断报告", "en": "ccwise Report"},
    "last":         {"zh": "最近",       "en": "Last"},
    "days_unit":    {"zh": "天",         "en": " days"},

    # ── Trend ──
    "by_week":      {"zh": "按周",       "en": "By Week"},
    "by_day":       {"zh": "按天",       "en": "By Day"},
    "week_col":     {"zh": "周",         "en": "Week"},
    "trend_col":    {"zh": "趋势",       "en": "Trend"},
    "date_col":     {"zh": "日期",       "en": "Date"},
    "commits_col":  {"zh": "提交",       "en": "Cmts"},
    "msgs_col":     {"zh": "消息",       "en": "Msgs"},
    "flags_col":    {"zh": "异常",       "en": "Flags"},
    "hourly":       {"zh": "时段分布",   "en": "Hourly"},
    "peak":         {"zh": "高峰",       "en": "Peak"},
    "hour_suffix":  {"zh": "时",         "en": "h"},
    "conv_flag":    {"zh": "次对话",     "en": "conv"},
    "err_flag":     {"zh": "错误",       "en": "err"},
    "cmt_flag":     {"zh": "提交",       "en": "cmt"},
    # 周标签格式："{wk}" 会被替换成实际日期字符串
    "week_label":   {"zh": "{wk}起",     "en": "W/{wk}"},
    "enum_sep":     {"zh": "、",         "en": ", "},

    # ── Projects ──
    "project_usage":  {"zh": "项目消耗",     "en": "Project Usage"},
    "project_col":    {"zh": "项目",         "en": "Project"},
    "cost_share_col": {"zh": "费用 / 占比",  "en": "Cost / Share"},
    "sess_cmt_col":   {"zh": "对话/提交",    "en": "Sess/Cmt"},
    "lines_col":      {"zh": "增 / 删",      "en": "+/-Lines"},
    "lang_col":       {"zh": "语言",         "en": "Lang"},
    "diag_col":       {"zh": "诊断",         "en": "Status"},
    "tag_efficient":  {"zh": "高效",         "en": "Efficient"},
    "tag_low":        {"zh": "低产",         "en": "Low output"},
    "tag_errors":     {"zh": "错误",         "en": "Errors"},

    # ── Tools ──
    "tool_usage":   {"zh": "工具调用统计", "en": "Tool Usage"},
    "tool_col":     {"zh": "工具",         "en": "Tool"},
    "calls_col":    {"zh": "调用",         "en": "Calls"},
    "share_col":    {"zh": "占比",         "en": "Share"},
    "bar_col":      {"zh": "分布",         "en": "Bar"},
    "tips_col":     {"zh": "效率提示",     "en": "Tips"},
    "total_calls":  {"zh": "共 {n} 次工具调用", "en": "Total {n} tool calls"},
    "tip_agent":    {"zh": "Agent 昂贵，检查是否可精简",
                     "en": "Agent is costly, consider reducing"},
    "tip_read_edit":{"zh": "Read/Edit={r}:1 偏高，定位前应更精确",
                     "en": "Read/Edit={r}:1 is high, be more precise before reading"},
    "tip_grep":     {"zh": "搜索频繁，考虑在 CLAUDE.md 写明项目结构",
                     "en": "High search count — document project structure in CLAUDE.md"},
    "tip_bash":     {"zh": "Bash 偏多，检查是否在用 cat/sed/echo 替代 Read/Edit",
                     "en": "High Bash usage — avoid cat/sed/echo, use Read/Edit instead"},

    # ── Diagnosis ──
    "issues":          {"zh": "问题诊断",     "en": "Issues"},
    "prob_sessions":   {"zh": "问题对话",     "en": "Problem Sessions"},
    "first_prompt":    {"zh": "首条 Prompt",  "en": "First Prompt"},
    "issue_col":       {"zh": "问题",         "en": "Issue"},
    "empty":           {"zh": "空",           "en": "empty"},
    "proj_friction":   {"zh": "项目摩擦（具体方案见 AI 诊断）",
                        "en": "Project Friction (see AI suggestions)"},
    "friction_count":  {"zh": "次数",         "en": "Count"},
    "friction_types":  {"zh": "主要问题类型", "en": "Friction Types"},
    "md_exists":       {"zh": "已有",         "en": "exists"},
    "md_missing":      {"zh": "缺失",         "en": "missing"},

    # ── MCP ──
    "mcp_title":       {"zh": "MCP 使用分析",  "en": "MCP Usage"},
    "mcp_usage_col":   {"zh": "使用情况",      "en": "Usage"},
    "mcp_tools_col":   {"zh": "工具明细",      "en": "Tools"},
    "mcp_action_col":  {"zh": "操作",          "en": "Action"},
    "mcp_global":      {"zh": "全局",          "en": "global"},
    "mcp_project":     {"zh": "项目级",        "en": "project"},
    "mcp_calls":       {"zh": "次调用",        "en": "calls"},
    "mcp_sess":        {"zh": "对话",          "en": "sess"},
    "mcp_no_calls":    {"zh": "无调用记录",    "en": "no calls"},
    "mcp_remove":      {"zh": "建议删除全局配置", "en": "remove from global"},
    "mcp_move":        {"zh": "移到项目级",    "en": "move to project"},
    "mcp_on_demand":   {"zh": "已按需加载",    "en": "on-demand"},
    "mcp_caption":     {"zh": "全局MCP每次对话都加载进context → vim ~/.claude/config.json 删除 {waste}",
                        "en": "Global MCPs load every session → remove from ~/.claude/config.json: {waste}"},

    # ── Env vars ──
    "env_title":       {"zh": "环境变量优化",         "en": "Env Var Suggestions"},
    "env_cmd_col":     {"zh": "export 命令（可直接复制）", "en": "export command (copy & paste)"},
    "env_status_col":  {"zh": "状态",                  "en": "Status"},
    "env_effect_col":  {"zh": "效果",                  "en": "Effect"},
    "not_set":         {"zh": "未设置",                "en": "not set"},
    "current_val":     {"zh": "当前",                  "en": "current"},
    "zshrc_hint":      {"zh": "加入 ~/.zshrc 后执行 source ~/.zshrc 生效",
                        "en": "Add to ~/.zshrc then run: source ~/.zshrc"},

    # ── AI ──
    "ai_title":        {"zh": "AI 诊断建议",            "en": "AI Suggestions"},
    "ai_calling":      {"zh": "调用 claude -p ...",     "en": "Calling claude -p ..."},
    "ai_unavailable":  {"zh": "AI 不可用：未安装 claude CLI",
                        "en": "AI unavailable: claude CLI not found"},
    "ai_timeout":      {"zh": "AI 超时（{s}s）",        "en": "AI timed out ({s}s)"},

    # ── Settings ──
    "config_guide":    {"zh": "配置指南",       "en": "Config Guide"},
    "cfg_category":    {"zh": "配置项",         "en": "Category"},
    "cfg_value":       {"zh": "值 / 命令",      "en": "Value / Command"},
    "cfg_desc":        {"zh": "说明",           "en": "Description"},
    "cfg_env":         {"zh": "环境变量",       "en": "Env vars"},
    "cfg_model":       {"zh": "默认模型",       "en": "Default model"},
    "cfg_mcp":         {"zh": "MCP 管理",       "en": "MCP"},
    "cfg_quota":       {"zh": "配额机制",       "en": "Quota"},
    "cfg_commands":    {"zh": "日常命令",       "en": "Commands"},

    # ── Settings descriptions ──
    "cfg_autocompact": {"zh": "上下文到 65% 自动压缩",    "en": "Auto-compact at 65% context"},
    "cfg_thinking":    {"zh": "限制思考量",               "en": "Cap thinking tokens"},
    "cfg_bg":          {"zh": "关闭后台调用",             "en": "Disable background model calls"},
    "cfg_model_desc":  {"zh": "日常用 Sonnet，复杂任务 /model opus",
                        "en": "Use Sonnet daily, /model opus for complex tasks"},
    "cfg_mcp_global":  {"zh": "全局 config.json 只留高频 MCP",
                        "en": "Keep only high-frequency MCPs in global config.json"},
    "cfg_mcp_proj":    {"zh": "低频的放项目级 .claude/settings.json",
                        "en": "Move low-frequency ones to project .claude/settings.json"},
    "cfg_mcp_ctx":     {"zh": "看每个 MCP 占多少 context window",
                        "en": "Check MCP context window usage"},
    "cfg_quota_win":   {"zh": "5 小时滚动窗口",          "en": "5-hour rolling window"},
    "cfg_quota_week":  {"zh": "周限额叠加在窗口之上",    "en": "Weekly quota on top of window"},
    "cfg_quota_hard":  {"zh": "无法设置每天/每小时硬限制", "en": "Cannot set per-day/per-hour hard limits"},
    "cfg_clear":       {"zh": "切换任务时清空上下文",    "en": "Clear context when switching tasks"},
    "cfg_compact":     {"zh": "长对话中压缩历史",        "en": "Compact history in long conversations"},
    "cfg_context":     {"zh": "检查当前上下文占用",      "en": "Check current context usage"},

    # ── Diagnosis labels ──
    "diag_context_bloat":  {"zh": "上下文膨胀", "en": "Context bloat"},
    "diag_no_commit":      {"zh": "无提交",     "en": "No commits"},
    "diag_heavy_single":   {"zh": "单轮过重",   "en": "Heavy single turn"},
    "diag_many_errors":    {"zh": "工具错误多", "en": "Many tool errors"},

    # ── Friction names ──
    "friction_wrong_approach":      {"zh": "方向跑偏",   "en": "Wrong approach"},
    "friction_buggy_code":          {"zh": "代码bug",    "en": "Buggy code"},
    "friction_misunderstood":       {"zh": "理解偏差",   "en": "Misunderstood"},
    "friction_api_error":           {"zh": "接口失败",   "en": "API error"},
    "friction_deploy":              {"zh": "部署失败",   "en": "Deploy failure"},
    "friction_excessive":           {"zh": "过度修改",   "en": "Excessive changes"},
    "friction_rejected":            {"zh": "操作被拒",   "en": "Action rejected"},
    "friction_wrong_lang":          {"zh": "语言错误",   "en": "Wrong language"},
    "friction_incomplete":          {"zh": "交付不全",   "en": "Incomplete"},
    "friction_limited_ctx":         {"zh": "上下文不足", "en": "Limited context"},
    "friction_repeated":            {"zh": "重复提问",   "en": "Repeated question"},

    # ── Env var descriptions ──
    "env_autocompact": {"zh": "上下文到 65% 自动压缩",    "en": "Auto-compact at 65% context"},
    "env_thinking":    {"zh": "限制思考量",               "en": "Cap thinking tokens"},
    "env_bg":          {"zh": "关闭后台调用",             "en": "Disable background model calls"},
}


def set_lang(lang: str):
    global _lang
    _lang = lang.lower()


def is_en() -> bool:
    return _lang == "en"


def t(key: str, **kwargs) -> str:
    """查找翻译键，返回当前语言对应字符串；支持 {placeholder} 插值。"""
    entry = STRINGS.get(key)
    if not entry:
        return key  # 未找到时原样返回 key，便于调试
    text = entry.get(_lang) or entry.get("zh", key)
    return text.format(**kwargs) if kwargs else text

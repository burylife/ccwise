"""所有映射常量集中管理（UI 文字统一走 lang.t()）"""

from .lang import t

# 摩擦类型 key → lang key 映射
FRICTION_KEY = {
    "wrong_approach":      "friction_wrong_approach",
    "buggy_code":          "friction_buggy_code",
    "misunderstood_request": "friction_misunderstood",
    "api_error":           "friction_api_error",
    "api_errors":          "friction_api_error",
    "deployment_failures": "friction_deploy",
    "excessive_changes":   "friction_excessive",
    "user_rejected_action":"friction_rejected",
    "wrong_language":      "friction_wrong_lang",
    "incomplete_work":     "friction_incomplete",
    "incomplete_delivery": "friction_incomplete",
    "limited_context":     "friction_limited_ctx",
    "repeated_question":   "friction_repeated",
}

# 问题对话诊断 key → lang key 映射
DIAGNOSIS_KEY = {
    "context_bloat": "diag_context_bloat",
    "no_commit":     "diag_no_commit",
    "heavy_single":  "diag_heavy_single",
    "many_errors":   "diag_many_errors",
}

# 推荐的环境变量（变量名, 推荐值, lang key）
ENV_VARS = [
    ("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", "65",  "env_autocompact"),
    ("MAX_THINKING_TOKENS",             "8000", "env_thinking"),
    ("DISABLE_NON_ESSENTIAL_MODEL_CALLS","1",   "env_bg"),
]

# 语言简写（在项目表中节省空间）
LANG_SHORT = {
    "Python": "Py", "TypeScript": "TS", "JavaScript": "JS",
    "Dart": "Dart", "Markdown": "MD", "HTML": "HTML", "CSS": "CSS",
    "Shell": "Sh", "YAML": "YAML", "JSON": "JSON",
    "Rust": "Rs", "Go": "Go", "Java": "Java", "Swift": "Sw",
}

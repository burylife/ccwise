"""多模型定价 + 单 session 费用计算"""

USD_TO_CNY = 7.2  # 估算人民币汇率

# 各模型族定价（$ per 1M tokens）
PRICES = {
    "opus": {"input": 15.0, "cache_create": 18.75, "cache_read": 1.5,  "output": 75.0},
    "sonnet": {"input": 3.0,  "cache_create": 3.75,  "cache_read": 0.30, "output": 15.0},
    "haiku": {"input": 0.80, "cache_create": 1.00,  "cache_read": 0.08, "output": 4.0},
}

# 兼容旧代码：按 Opus 定价
PRICE_INPUT = PRICES["opus"]["input"]
PRICE_CACHE_CREATE = PRICES["opus"]["cache_create"]
PRICE_CACHE_READ = PRICES["opus"]["cache_read"]
PRICE_OUTPUT = PRICES["opus"]["output"]


def _tier(model_name: str) -> dict:
    """根据模型名返回定价表"""
    n = model_name.lower()
    if "opus" in n:
        return PRICES["opus"]
    if "haiku" in n:
        return PRICES["haiku"]
    return PRICES["sonnet"]


def session_cost(s) -> float:
    """按实际模型计算等价 API 费用（USD）。
    优先使用 model_usage 精确计算；无该字段时回退到 top-level token 字段（Sonnet 估算）。"""
    mu = s.get("model_usage")
    if mu:
        total = 0.0
        for model, u in mu.items():
            p = _tier(model)
            total += (u["input"] / 1e6 * p["input"]
                      + u["cache_create"] / 1e6 * p["cache_create"]
                      + u["cache_read"] / 1e6 * p["cache_read"]
                      + u["output"] / 1e6 * p["output"])
        return total
    p = PRICES["sonnet"]
    return (s.get("input_tokens", 0) / 1e6 * p["input"]
            + s.get("cache_create", 0) / 1e6 * p["cache_create"]
            + s.get("cache_read", 0) / 1e6 * p["cache_read"]
            + s.get("output_tokens", 0) / 1e6 * p["output"])


def format_cost(c):
    """统一的费用格式化：≥10 用整数加粗，1~10 一位小数，<1 两位小数"""
    if c >= 10:
        return f"[bold]${c:.0f}[/bold]"
    if c >= 1:
        return f"${c:.1f}"
    return f"${c:.2f}"

# ccwise

Claude Code 本地用量分析工具 — 读取 `~/.claude/projects/*.jsonl` 数据，输出可操作的费用与效率洞察。

英文版：[README.en.md](README.en.md)

## 功能

- **精准费用计算** — 按实际模型（Opus / Sonnet / Haiku）分别定价，覆盖四种 token 类型：input、cache_write、cache_read、output
- **多维聚合** — 按周、按天、按小时、按项目、按工具、按 MCP 服务统计
- **问题诊断** — 标记上下文膨胀、高费用无提交、工具错误频繁等异常对话
- **AI 建议** — 调用 `claude -p` 生成针对高摩擦项目的 CLAUDE.md 规则和 hook 命令
- **MCP 浪费检测** — 找出全局配置但从未实际调用的 MCP 服务
- **环境变量推荐** — 打印可直接粘贴的 `export` 命令

## 安装

```bash
git clone <repo> ccwise
cd ccwise
python3 -m venv .venv
source .venv/bin/activate
pip install rich
```

## 使用

```bash
# 默认：最近 30 天，带 AI 建议
./run.sh

# 指定时间范围
./run.sh -d 7
./run.sh --days 90

# 按项目过滤
./run.sh -p lazyhappy

# 跳过 AI（更快）
./run.sh --no-ai

# 英文输出
./run.sh --en

# 底部显示配置指南
./run.sh --settings

# 组合使用
./run.sh -d 7 --no-ai --en
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-d, --days N` | 分析最近 N 天 | 30 |
| `-p, --project NAME` | 按项目名称或路径过滤 | — |
| `--no-ai` | 跳过 `claude -p` 调用 | 开启 AI |
| `--en` | 英文输出 | 中文 |
| `--settings` | 显示配置指南表格 | 关闭 |

## 报告结构

1. **摘要面板** — 状态、总 token、费用（USD）、对话数、日均、错误率、缓存命中率、模型分布
2. **按周** — 每周费用、token、对话、消息、提交数，带趋势条
3. **按天** — 每天费用、token、消息数、异常标记
4. **时段热力图** — 24 小时活跃度分布，标注高峰时段
5. **项目消耗** — 按费用排名前 10 项目，含对话/提交/代码行/语言明细和效率标签
6. **工具调用统计** — 按调用次数排名前 10 工具，附效率提示
7. **问题诊断**
   - 问题对话：标记上下文膨胀、无提交、工具错误多等
   - 项目摩擦：来自 facets 数据的摩擦类型明细，检查 CLAUDE.md 存在性
   - MCP 分析：每个服务的调用次数和操作建议
   - 环境变量建议：未设置的变量及可复制的 export 命令
8. **AI 建议**（默认开启）— 调用 `claude -p`，返回具体的 CLAUDE.md 规则和 shell 命令
9. **配置指南**（`--settings`）— 常用 Claude Code 优化项快速参考表

## 数据来源

| 路径 | 内容 |
|------|------|
| `~/.claude/projects/*/*.jsonl` | 主数据源，每个对话一个文件 |
| `~/.claude/usage-data/session-meta/*.json` | git 提交、代码行变更、语言 |
| `~/.claude/usage-data/facets/*.json` | 摩擦与满意度数据 |
| `~/.claude/config.json` | 全局 MCP 服务配置 |

## 项目结构

```
ccwise/
├── ccwise.py              # CLI 入口
├── run.sh                 # 激活 venv 并运行 ccwise.py
├── README.md              # 中文文档
├── README.en.md           # English documentation
└── ccwise_lib/
    ├── lang.py            # 语言设置 + 全部 UI 字符串翻译
    ├── labels.py          # 键值映射（摩擦类型、诊断标签、环境变量）
    ├── loader.py          # JSONL 解析 + session-meta 合并
    ├── pricing.py         # 按模型定价 + 对话费用计算
    ├── utils.py           # 日期工具、token 格式化、项目名解析
    ├── overview.py        # 摘要面板
    ├── trend.py           # 周/天/时段视图
    ├── projects.py        # 项目消耗表格
    ├── tools.py           # 工具调用统计
    ├── diagnosis.py       # 问题对话、摩擦、MCP、环境变量
    ├── ai.py              # claude -p 调用 + Markdown 渲染
    └── settings.py        # 配置指南表格
```

## 设计原则

- **真实数据** — 不补充虚拟行；缺失数据显示为 `-`
- **可操作输出** — 每条建议都是可直接粘贴的命令或规则
- **模型感知定价** — Opus / Sonnet / Haiku 每次对话按实际模型分别计费
- **智能项目合并** — 同一父目录下的兄弟 git 仓库自动合并（如 `yuewu/app` + `yuewu/backend` → `yuewu`）；叶名匹配处理备用克隆路径
- **本地时区** — 所有日期比较使用本地时间，而非 UTC

## 说明

- 费用显示的是**等效 API 价格**，不是订阅者实际支付的金额。用于衡量使用价值和项目对比，不作为账单依据。
- `cache_read` token 主导总 token 数属于正常现象；每次对话轮次都会重新读取缓存的上下文。
- `--en` 切换所有 UI 标签为英文，首条 Prompt 内容保持原语言（来自对话历史）。

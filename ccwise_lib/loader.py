"""数据加载层

- jsonl 主源（~/.claude/projects/*.jsonl）：提供完整 token、cwd、工具调用，覆盖全部 session
- session-meta 增强（~/.claude/usage-data/session-meta/*.json）：提供 git_commits / languages /
  lines_added / files_modified 等字段，按 session_id 合并到 jsonl session 上
- facets（~/.claude/usage-data/facets/*.json）：摩擦/满意度分析数据
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from .utils import dir_to_path, pname

CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"
META_DIR = CLAUDE_DIR / "usage-data" / "session-meta"
FACETS_DIR = CLAUDE_DIR / "usage-data" / "facets"

# 文件扩展名 → 语言（用于 session-meta 没覆盖到的新 session）
EXT_TO_LANG = {
    ".py": "Python", ".pyi": "Python",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
    ".dart": "Dart", ".go": "Go", ".rs": "Rust", ".java": "Java",
    ".kt": "Kotlin", ".swift": "Swift", ".rb": "Ruby", ".php": "PHP",
    ".c": "C", ".h": "C", ".cpp": "C++", ".cc": "C++", ".hpp": "C++",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
    ".md": "Markdown", ".html": "HTML", ".css": "CSS", ".scss": "CSS",
    ".yaml": "YAML", ".yml": "YAML", ".json": "JSON", ".toml": "TOML",
    ".sql": "SQL", ".vue": "Vue", ".svelte": "Svelte",
}


def _empty_session(proj_path, session_id):
    return {
        "project_path": proj_path,
        "session_id": session_id,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_create": 0,
        "cache_read": 0,
        "total_tokens": 0,
        "start_time": "",
        "user_message_count": 0,
        "tool_counts": defaultdict(int),
        "tool_errors": 0,
        "tool_error_counts": defaultdict(int),  # 每个工具的错误次数
        "git_commits": 0,
        "lines_added": 0,
        "lines_removed": 0,
        "files_modified": 0,
        "_files_set": set(),       # 内部用：去重文件路径
        "languages": defaultdict(int),
        "first_prompt": "",
        "duration_minutes": 0,
        "message_hours": [],       # 各 user 消息的本地小时（用于时段热力图）
        "model_usage": {},         # model_name → {input,cache_create,cache_read,output}
    }


def _parse_jsonl(jsonl_path, proj_path):
    """解析单个 jsonl 文件，返回 session dict"""
    session = _empty_session(proj_path, jsonl_path.stem)
    last_time = ""
    _pending_tool_ids: dict[str, str] = {}  # tool_use_id → tool_name，用于错误溯源
    try:
        with open(jsonl_path) as fh:
            for line in fh:
                d = json.loads(line)
                msg_type = d.get("type", "")

                if msg_type == "assistant":
                    msg = d.get("message", {})
                    usage = msg.get("usage", {})
                    inp = usage.get("input_tokens", 0)
                    cc  = usage.get("cache_creation_input_tokens", 0)
                    cr  = usage.get("cache_read_input_tokens", 0)
                    out = usage.get("output_tokens", 0)
                    session["input_tokens"] += inp
                    session["output_tokens"] += out
                    session["cache_create"] += cc
                    session["cache_read"] += cr
                    # 按模型分桶，用于精确定价
                    model = msg.get("model", "unknown")
                    mu = session["model_usage"].setdefault(
                        model, {"input": 0, "cache_create": 0, "cache_read": 0, "output": 0})
                    mu["input"] += inp
                    mu["cache_create"] += cc
                    mu["cache_read"] += cr
                    mu["output"] += out
                    # cwd 是真实项目路径，比目录名反推可靠
                    real_cwd = d.get("cwd", "")
                    if real_cwd:
                        session["project_path"] = real_cwd
                    # 工具调用：统计调用次数 + 记录 tool_use_id 以便后续错误溯源
                    for block in msg.get("content", []) or []:
                        if not (isinstance(block, dict) and block.get("type") == "tool_use"):
                            continue
                        tname = block.get("name", "?")
                        tid = block.get("id", "")
                        if tid:
                            _pending_tool_ids[tid] = tname
                        session["tool_counts"][tname] += 1
                        _extract_code_metrics(session, tname, block.get("input", {}))

                elif msg_type == "user":
                    session["user_message_count"] += 1
                    ts = d.get("timestamp", "")
                    if not session["start_time"]:
                        session["start_time"] = ts
                    if ts:
                        last_time = ts
                        # 记录本地小时，用于时段热力图
                        try:
                            h = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().hour
                            session["message_hours"].append(h)
                        except (ValueError, TypeError):
                            pass
                    # 第一条真正人类输入做 first_prompt（跳过系统注入，限 100 字防超长）
                    if not session["first_prompt"]:
                        text = _extract_text(d.get("message", {})).strip()
                        if text and not text.startswith("<"):
                            session["first_prompt"] = text[:100]
                    # tool_result 也是 type=user，在 content 里
                    msg = d.get("message", {})
                    for block in msg.get("content", []) or []:
                        if isinstance(block, dict) and block.get("type") == "tool_result":
                            if block.get("is_error"):
                                session["tool_errors"] += 1
                                tid = block.get("tool_use_id", "")
                                tname = _pending_tool_ids.get(tid, "unknown")
                                session["tool_error_counts"][tname] += 1
    except Exception:
        return None

    if not session["start_time"]:
        return None

    # 时长 = 最后一条 user 消息时间 - 第一条
    if last_time:
        try:
            t0 = datetime.fromisoformat(session["start_time"].replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(last_time.replace("Z", "+00:00"))
            session["duration_minutes"] = max(0, int((t1 - t0).total_seconds() / 60))
        except (ValueError, TypeError):
            pass

    session["total_tokens"] = (session["input_tokens"] + session["output_tokens"]
                               + session["cache_create"] + session["cache_read"])
    # 将内部 set 转为计数后删除，保持 session dict 可序列化
    session["files_modified"] = len(session.pop("_files_set"))
    return session


def _extract_text(msg):
    """从 user message 的 content 中提取首段文本"""
    if isinstance(msg, str):
        return msg
    if not isinstance(msg, dict):
        return ""
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                return block.get("text", "")
    return ""


def _count_lines(s):
    """文本的行数（空字符串算 0）"""
    if not s:
        return 0
    return s.count("\n") + (0 if s.endswith("\n") else 1)


def _extract_code_metrics(session, tname, inp):
    """从工具调用 input 提取 git_commits / lines_added / lines_removed / files"""
    if not isinstance(inp, dict):
        return
    if tname == "Bash":
        cmd = inp.get("command", "")
        # 计 git commit 次数（排除 git log/diff/show 等含 commit 子字符串的命令）
        if "git commit" in cmd and "git log" not in cmd and "git show" not in cmd:
            session["git_commits"] += 1
    elif tname == "Edit":
        old = inp.get("old_string", "")
        new = inp.get("new_string", "")
        session["lines_removed"] += _count_lines(old)
        session["lines_added"] += _count_lines(new)
        fp = inp.get("file_path", "")
        if fp:
            session["_files_set"].add(fp)
            ext = Path(fp).suffix.lower()
            lang = EXT_TO_LANG.get(ext)
            if lang:
                session["languages"][lang] += 1
    elif tname == "Write":
        session["lines_added"] += _count_lines(inp.get("content", ""))
        fp = inp.get("file_path", "")
        if fp:
            session["_files_set"].add(fp)
            ext = Path(fp).suffix.lower()
            lang = EXT_TO_LANG.get(ext)
            if lang:
                session["languages"][lang] += 1
    elif tname == "NotebookEdit":
        session["lines_added"] += _count_lines(inp.get("new_source", ""))
        session["lines_removed"] += _count_lines(inp.get("old_source", ""))


def _load_meta_index():
    """加载 session-meta，按 session_id 索引。这些字段由 Claude Code 自身的 hook 维护，
    覆盖 git_commits / lines_added / lines_removed / files_modified / languages。"""
    meta = {}
    if not META_DIR.exists():
        return meta
    for f in META_DIR.glob("*.json"):
        try:
            d = json.load(open(f))
            sid = d.get("session_id") or f.stem
            meta[sid] = d
        except Exception:
            pass
    return meta


def _merge_meta(session, meta):
    """合并 session-meta 字段。对计数字段取 max（哪个来源更全就用哪个），
    languages 直接累加 meta 提供的"""
    for k in ("git_commits", "git_pushes", "lines_added", "lines_removed", "files_modified"):
        v = meta.get(k, 0) or 0
        if v > session.get(k, 0):
            session[k] = v
    langs = meta.get("languages", {}) or {}
    if isinstance(langs, dict):
        for lang, cnt in langs.items():
            session["languages"][lang] += cnt


def load_sessions(days_filter=None):
    """扫描 projects 目录加载 session，再用 session-meta 增强字段。"""
    sessions = []
    cutoff_mtime = None
    if days_filter:
        cutoff_mtime = (datetime.now() - timedelta(days=days_filter + 1)).timestamp()

    if not PROJECTS_DIR.exists():
        return sessions

    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        proj_path = dir_to_path(proj_dir.name)
        for f in proj_dir.glob("*.jsonl"):
            if cutoff_mtime and f.stat().st_mtime < cutoff_mtime:
                continue
            s = _parse_jsonl(f, proj_path)
            if s:
                sessions.append(s)

    # 合并 session-meta（覆盖率不全，缺失的字段保持默认 0）
    meta_index = _load_meta_index()
    for s in sessions:
        meta = meta_index.get(s["session_id"])
        if meta:
            _merge_meta(s, meta)

    # 过滤无效 session（启动后未对话即关闭，tokens 全 0）
    sessions = [s for s in sessions if s["total_tokens"] > 0]
    sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
    return sessions


def load_facets():
    """加载 facets 数据（摩擦/满意度分析），按 session_id 索引"""
    facets = {}
    if not FACETS_DIR.exists():
        return facets
    for f in FACETS_DIR.glob("*.json"):
        try:
            d = json.load(open(f))
            facets[d.get("session_id", f.stem)] = d
        except Exception:
            pass
    return facets

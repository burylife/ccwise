"""通用辅助函数：日期、token 格式化、项目路径"""

import functools
from datetime import datetime
from pathlib import Path

# pname 的 git 根缓存（path → 项目名）
_PNAME_CACHE = {}


@functools.lru_cache(maxsize=64)
def _git_child_count(parent: Path) -> int:
    """计算 parent 下有多少个直接 git 子仓库（用于判断是否合并项目）"""
    try:
        return sum(1 for d in parent.iterdir()
                   if d.is_dir() and (d / ".git").exists())
    except OSError:
        return 999


def local_date(iso_str):
    """UTC 时间字符串 → 本地日期字符串 YYYY-MM-DD"""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return iso_str[:10]


def tok(n):
    """大数字简写：4.9B / 1.3M / 45K / 1.2K"""
    if n >= 1_000_000_000:
        return f"{n / 1e9:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1e6:.0f}M" if n >= 10_000_000 else f"{n / 1e6:.1f}M"
    if n >= 10_000:
        return f"{n / 1000:.0f}K"
    if n >= 1_000:
        return f"{n / 1000:.1f}K"
    return str(int(n))


def _resolve_worktree(git_file):
    """worktree 的 .git 是文件，内容形如 'gitdir: /主仓/.git/worktrees/xxx'。
    解析后返回主仓库目录，否则返回 None。"""
    try:
        content = git_file.read_text().strip()
        if content.startswith("gitdir:"):
            gitdir = content.split(":", 1)[1].strip()
            # gitdir 通常是 /主仓/.git/worktrees/xxx
            idx = gitdir.find("/.git/")
            if idx > 0:
                return Path(gitdir[:idx])
    except (OSError, ValueError):
        pass
    return None


def pname(path):
    """按 git 根聚合项目名。优先级：
    1. cwd 向上找 .git；worktree (.git 是文件) 解析到主仓库
    2. cwd 路径含 `worktrees` 段：用前一段作项目名（已删除的 worktree 也能聚合）
    3. 路径末两段（保留上层目录作上下文）
    结果以 git 根的末两段输出。"""
    if not path:
        return path
    cached = _PNAME_CACHE.get(path)
    if cached is not None:
        return cached

    p = Path(path)

    # 1. 向上找 .git
    cur = p
    git_root = None
    for _ in range(20):
        git_path = cur / ".git"
        if git_path.exists():
            if git_path.is_file():
                main = _resolve_worktree(git_path)
                git_root = main if main else cur
            else:
                git_root = cur
            break
        if cur == cur.parent:
            break
        cur = cur.parent

    if git_root:
        parts = git_root.parts
        parent = git_root.parent
        siblings = _git_child_count(parent)
        # 2-4 个兄弟 git 仓库 → 父目录是真正的项目容器（如 yuewu/），合并显示
        # 5 个以上 → 父目录是通用容器（如 python/），保持 parent/repo 格式
        if 2 <= siblings <= 4 and len(parts) >= 2:
            result = parts[-2]  # 只用父目录名，如 "yuewu"
        else:
            result = "/".join(parts[-2:]) if len(parts) >= 2 else str(git_root)
    elif "worktrees" in p.parts:
        # 2. 已删除的 worktree：从路径模式还原仓库名
        idx = p.parts.index("worktrees")
        if idx >= 1:
            repo_end = idx  # worktrees 前一段是仓库名
            start = max(0, repo_end - 2)
            result = "/".join(p.parts[start:repo_end])
        else:
            result = "/".join(p.parts[-2:])
    else:
        # 3. 回退
        result = "/".join(p.parts[-2:]) if len(p.parts) >= 2 else path

    _PNAME_CACHE[path] = result
    return result


def dir_to_path(dirname):
    """projects 目录名 → 原始路径：-Users-burylife-dev → /Users/burylife/dev"""
    parts = dirname.split("-")
    return "/" + "/".join(p for p in parts if p)

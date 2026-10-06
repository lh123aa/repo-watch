#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
repo_watch.py — 后台监控本机所有开源 (git) 项目更新
=====================================================
功能:
  1. 自动扫描指定盘符下正在使用的 git 仓库 (带排除规则 + 缓存加速)
  2. 检查默认分支是否落后于远端 (轻量 git ls-remote)
  3. 有更新时弹出 Windows 系统横幅通知 (仅系统通知, 不占终端)
  4. 点通知 → 在系统托盘/弹窗征求同意 → 自动 git pull; 脏工作区跳过并警告
  5. 常驻后台循环, 开机任务计划自动拉起

依赖:  系统已安装 git + python3;  `pip install win10toast`
用法:  python repo_watch.py            # 常驻
       python repo_watch.py --once     # 检查一次后退出
       python repo_watch.py --list     # 仅列出发现的仓库
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Windows 系统通知
try:
    from win10toast import ToastNotifier
    TOAST_OK = True
except Exception:
    TOAST_OK = False
    class ToastNotifier:
        def show_toast(self, *a, **k): pass

IS_WIN = (platform.system() == "Windows")
SCRIPT_DIR = Path(__file__).resolve().parent
STATE_FILE = SCRIPT_DIR / "repo_watch_state.json"
CONFIG_FILE = SCRIPT_DIR / "repo_watch.config.json"

# ---------------- 配置 (可按需修改) ----------------
CONFIG = {
    # 要扫描的盘符 (自动检测存在的)
    "drives": None,            # None = 自动检测全部固定盘
    # 每 N 分钟扫描一次 (常驻模式)
    "interval_minutes": 30,
    # 脏工作区处理: skip = 跳过并警告 (当前实现)
    "dirty_policy": "skip",
    # 通知停留秒数
    "toast_display_len": 10,
    # GitHub Token (可选, 用于私有仓库与更高 API 限流; 也可用环境变量 GITHUB_TOKEN)
    "github_token": os.environ.get("GITHUB_TOKEN", ""),
}


def load_local_config():
    """读取本地配置文件 (setup.bat 写入的 Token 等), 覆盖默认 CONFIG.
    仅覆盖存在的键, 不删除其他键."""
    global CONFIG
    if not CONFIG_FILE.exists():
        return
    try:
        raw = CONFIG_FILE.read_bytes()
        text = raw.decode("utf-8-sig", errors="replace")  # 容忍 BOM
        data = json.loads(text)
        for k, v in data.items():
            if v is not None:
                CONFIG[k] = v
    except Exception as e:
        print(f"[repo-watch] 读取本地配置失败: {e}", file=sys.stderr)

# 扫描时自动排除的目录名 (加速)
EXCLUDE_DIR_NAMES = {
    "node_modules", ".git", "venv", ".venv", "env", "Env",
    ".cache", "__pycache__", ".tox", "site-packages",
    "dist", "build", "target", "out", ".idea", ".vs",
}

# 非项目常见的巨大系统目录 (全盘扫描时跳过, 避免 C 盘扫描过慢/越权)
SKIP_TOP_DIRS = {
    "Windows", "Program Files", "Program Files (x86)", "ProgramData",
    "Recovery", "PerfLogs", "Intel", "Config.Msi", "inetpub",
}

# 已知 "非开源" 或系统级仓库的 remote 排除 (可选, 留空则全部监控)
REMOTE_BLOCKLIST = []

# 仓库路径去重: 同一 remote 只保留最早 (最浅) 的路径
# 本地状态缓存
STATE = {"repos": {}, "seen": {}, "checked_remotes": {}}


# ---------------- 工具函数 ----------------
def log(msg):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{stamp}] {msg}", flush=True)


def run_git(args, cwd, timeout=60):
    """运行 git 命令, 返回 (returncode, stdout+stderr)."""
    try:
        p = subprocess.run(
            ["git", "-c", "core.quotepath=false"] + args,
            cwd=str(cwd), capture_output=True, timeout=timeout,
            text=True, errors="replace",
        )
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, "timeout"
    except Exception as e:
        return -1, str(e)


def is_fixed_drive(root):
    """判断路径是否为 Windows 固定磁盘 (含正在使用的)."""
    if not IS_WIN:
        return True
    try:
        import ctypes
        DRIVE_FIXED = 3
        DRIVE_REMOVABLE = 2
        drive = (root or "C:\\")[:2].upper()
        if not drive.endswith("\\"):
            drive += "\\"
        flags = ctypes.windll.kernel32.GetDriveTypeW(drive)
        return flags in (DRIVE_FIXED, DRIVE_REMOVABLE)
    except Exception:
        return True


def detect_drives():
    """检测本机存在的盘符, 返回根路径列表."""
    if not IS_WIN:
        return ["/"]
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        root = f"{letter}:\\"
        if os.path.exists(root) and is_fixed_drive(root):
            drives.append(root)
    return drives


def find_git_repos(root):
    """在 root 下找所有 .git 目录 (剪枝排除, 限制深度). 生成器, 逐个产出路径."""
    root = Path(root)
    # 全盘时跳过系统大目录
    if root.is_dir() and root.name in SKIP_TOP_DIRS:
        return
    # 逐层遍历, 遇到 .git 记录, 不深入其内部
    # 用 os.walk 配合剪枝 (原地修改 dirs)
    max_depth = 8 if str(root).endswith("\\") and len(str(root)) <= 3 else 12
    start = root
    root_str = str(start)
    for cur, dirs, _files in os.walk(start, topdown=True, onerror=lambda e: None):
        # 计算深度
        rel = os.path.relpath(cur, root_str)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth >= max_depth:
            dirs[:] = []
            continue
        # 剪枝
        pruned = []
        for d in dirs:
            if d in EXCLUDE_DIR_NAMES:
                continue
            # 全盘扫描时顶层跳过系统大目录
            if depth == 0 and d in SKIP_TOP_DIRS:
                continue
            pruned.append(d)
        dirs[:] = pruned
        # 当前目录本身是 git 仓库?
        git_dir = os.path.join(cur, ".git")
        if os.path.exists(git_dir):
            yield cur
            # 不继续深入仓库内部找嵌套
            dirs[:] = []


def get_repo_info(path):
    """获取仓库的 origin / upstream remote 与默认分支."""
    rc, out = run_git(["remote", "-v"], path, timeout=15)
    origin = ""
    upstream = ""
    for line in out.splitlines():
        m = re.match(r"(\S+)\s+(\S+)\s+\(fetch\)", line)
        if not m:
            m = re.match(r"(\S+)\s+(\S+)", line.strip())
            if not m:
                continue
        name, url = m.group(1), m.group(2)
        if name == "origin" and not origin:
            origin = url
        elif name == "upstream" and not upstream:
            upstream = url
    # 默认分支: 优先读 HEAD 指向
    rc2, head_out = run_git(["symbolic-ref", "--short", "HEAD"], path, timeout=15)
    default_branch = head_out.strip() if rc2 == 0 and head_out.strip() else "main"
    return origin, upstream, default_branch


def parse_github_owner(remote):
    """从 GitHub remote 解析 owner/repo. 支持 SSH 与 HTTPS."""
    if not remote:
        return None
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", remote)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return None


def is_dirty(path):
    """判断工作区是否有未提交改动."""
    rc, out = run_git(["status", "--porcelain"], path, timeout=20)
    if rc == 0 and out.strip():
        return True
    return False


def local_head(path):
    rc, out = run_git(["rev-parse", "HEAD"], path, timeout=15)
    return out.strip() if rc == 0 else None


def remote_head(path, branch, remote_name="origin"):
    """轻量取远端分支 HEAD (不 pull, 不 fetch 全量). 指定 remote 名."""
    rc, out = run_git(["ls-remote", remote_name, f"refs/heads/{branch}"], path, timeout=30)
    if rc == 0 and out.strip():
        parts = out.strip().split()
        if parts:
            return parts[0]
    return None


def resolve_update_source(path, origin, upstream):
    """自动判断更新来源:
    - 有 upstream remote (fork 场景) → 拉 upstream 的上游原始仓库
    - 否则 → 拉 origin (对别人的项目, origin 即上游; 对自己项目, origin 即自己)
    返回 (remote_name, gh_owner_repo). gh 用于 API 拉详情.
    """
    if upstream:
        gh_up = parse_github_owner(upstream)
        if gh_up:
            return "upstream", gh_up
        # upstream 不是 GitHub, 退回到 origin
        return "origin", parse_github_owner(origin)
    return "origin", parse_github_owner(origin)


def upstream_default_branch(gh):
    """用 GitHub API 探测某仓库的真实默认分支 (用于 fork 拉上游). 失败回退 main."""
    if not gh:
        return "main"
    try:
        import urllib.request
        token = CONFIG["github_token"]
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(f"https://api.github.com/repos/{gh}", headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data.get("default_branch", "main")
    except Exception:
        return "main"


def fetch_release_and_commits(path, repo, default_branch):
    """拉取 GitHub release notes + 最近 commits. 失败返回 None."""
    token = CONFIG["github_token"]
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    results = {"releases": [], "commits": []}
    try:
        import urllib.request
        base = f"https://api.github.com/repos/{repo}"
        # 最新 3 个 release
        req = urllib.request.Request(base + "/releases?per_page=3", headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        for rel in data:
            results["releases"].append({
                "tag": rel.get("tag_name", ""),
                "name": rel.get("name", rel.get("tag_name", "")),
                "body": (rel.get("body") or "")[:800],
            })
        # 默认分支最近 5 条 commit
        req2 = urllib.request.Request(base + f"/commits?per_page=5&sha={default_branch}", headers=headers)
        with urllib.request.urlopen(req2, timeout=15) as r2:
            cdata = json.loads(r2.read().decode("utf-8"))
        for c in cdata:
            msg = (c.get("commit", {}).get("message") or "").splitlines()[0][:100]
            results["commits"].append({
                "sha": c.get("sha", "")[:7],
                "msg": msg,
                "date": c.get("commit", {}).get("committer", {}).get("date", ""),
            })
    except Exception as e:
        log(f"获取 {repo} 更新详情失败: {e}")
        return {"releases": [], "commits": []}
    return results


def build_update_text(name, info):
    """构造通知正文."""
    lines = [f"{name} 有更新"]
    if info.get("releases"):
        for rel in info["releases"][:2]:
            lines.append(f"🔖 {rel['name']}")
            if rel["body"]:
                lines.append(rel["body"].splitlines()[0][:60])
    if info.get("commits"):
        lines.append("最近提交:")
        for c in info["commits"][:3]:
            lines.append(f"  {c['sha']} {c['msg']}")
    return "\n".join(lines)


def notify(title, msg):
    """Windows 系统横幅通知."""
    if not TOAST_OK:
        log(f"(通知不可用) {title}: {msg}")
        return
    try:
        t = ToastNotifier()
        t.show_toast(
            title, msg,
            duration=CONFIG["toast_display_len"],
            threaded=False,
        )
    except Exception as e:
        log(f"通知发送失败: {e}")


def confirm_update_interactive(name, info, headless=False):
    """征求同意: 弹原生询问 (tkinter).
    headless=True (pythonw 后台常驻) 时若 tkinter 不可用, 直接返回 False,
    绝不回退到 input() —— 无控制台的后台进程没有 stdin, input() 会抛
    EOFError 卡死整个常驻循环。前台 (python 有控制台) 才允许终端确认。"""
    if IS_WIN:
        try:
            import tkinter as tk
            from tkinter import messagebox
            detail = build_update_text(name, info)
            root = tk.Tk()
            root.withdraw()
            root.lift()
            answer = messagebox.askyesno(
                "repo-watch 更新确认",
                f"{name} 发现更新, 是否自动执行 git pull?\n\n{detail}",
            )
            root.destroy()
            return answer
        except Exception as e:
            log(f"弹窗确认失败: {e}")
    if headless:
        log(f"{name} 后台模式无法弹确认窗, 跳过本次更新 (下一轮再试)")
        return False
    # 终端确认 (前台, 有控制台时)
    try:
        ans = input(f"是否更新 {name} ? [y/N] ").strip().lower()
        return ans == "y"
    except (EOFError, OSError):
        return False


def do_pull(path, name, branch, remote_name="origin"):
    """执行 git pull <remote> <branch>. 返回 (success, message)."""
    # 脏工作区检查
    if is_dirty(path):
        log(f"{name} 工作区有未提交改动, 跳过更新 (dirty skip)")
        notify(f"{name} 跳过", "工作区有未提交改动, 为安全跳过自动更新, 请手动处理。")
        return False, "dirty"
    log(f"{name} 开始 git pull {remote_name}/{branch} ...")
    rc, out = run_git(["pull", "--ff-only", remote_name, branch], path, timeout=120)
    if rc == 0:
        log(f"{name} 更新成功 (from {remote_name})")
        notify(f"{name} 已更新", f"git pull {remote_name}/{branch} 成功完成。")
        return True, "ok"
    else:
        log(f"{name} 更新失败: {out[:300]}")
        notify(f"{name} 更新失败", out.strip()[:200])
        return False, "fail"


def load_state():
    global STATE
    if STATE_FILE.exists():
        try:
            STATE.update(json.loads(STATE_FILE.read_text("utf-8")))
        except Exception:
            pass


def save_state():
    try:
        STATE_FILE.write_text(json.dumps(STATE, ensure_ascii=False, indent=2), "utf-8")
    except Exception as e:
        log(f"保存状态失败: {e}")


def discover_repos():
    """扫描所有盘, 返回 repo 信息列表 (含 origin/upstream 识别)."""
    drives = CONFIG["drives"] or detect_drives()
    log(f"扫描盘符: {drives}")
    found = {}
    for d in drives:
        t0 = time.time()
        count = 0
        for repo_path in find_git_repos(d):
            count += 1
            found[repo_path] = repo_path
            if count % 50 == 0:
                log(f"  {d} 已发现 {count} 个仓库 ...")
        log(f"  {d} 扫描完成, 共 {count} 个仓库, 耗时 {time.time()-t0:.1f}s")
    # 去重: 同一 remote 保留最浅路径 (避免 clone/fork/多副本重复监控)
    repos = []
    by_remote = {}  # remote_url -> {path, ...}
    for rp in found.values():
        origin, upstream, branch = get_repo_info(rp)
        remote = upstream or origin
        if not remote:
            continue
        if any(remote.startswith(b) or b.startswith(remote) for b in REMOTE_BLOCKLIST):
            continue
        gh = parse_github_owner(remote)
        entry = {
            "path": rp,
            "origin": origin,
            "upstream": upstream,
            "remote": remote,
            "branch": branch,
            "github": gh,
            "origin_gh": parse_github_owner(origin),
            "name": Path(rp).name,
        }
        # 同 remote 只保留最浅路径
        key = remote.lower()
        if key not in by_remote or rp.count(os.sep) < by_remote[key]["path"].count(os.sep):
            by_remote[key] = entry
    repos = list(by_remote.values())
    # 缓存
    STATE["repos"] = {r["remote"]: r["path"] for r in repos if r["github"]}
    STATE["seen"] = {rp: datetime.now().isoformat() for rp in found}
    save_state()
    log(f"共发现 {len(repos)} 个 git 仓库 (GitHub {sum(1 for r in repos if r['github'])}, "
        f"含 fork/upstream {sum(1 for r in repos if r['upstream'])})")
    return repos


def check_repos(repos):
    """检查所有仓库是否有更新, 自动判断更新来源 (upstream 优先, 回退 origin)."""
    updates = []
    for r in repos:
        try:
            # 自动识别: 有 upstream 拉 upstream 上游, 否则拉 origin
            remote_name, gh = resolve_update_source(r["path"], r["origin"], r["upstream"])
            if not gh:
                continue  # 非 GitHub 远端, 跳过
            # fork 场景: 探测上游真实默认分支; 普通场景: 本地默认分支
            if remote_name == "upstream":
                branch = upstream_default_branch(gh)
            else:
                branch = r["branch"]
            local = local_head(r["path"])
            remote = remote_head(r["path"], branch, remote_name)
            if local and remote and local != remote:
                log(f"🔔 {r['name']} ({gh}) 落后 via {remote_name}/{branch}: "
                    f"本地 {local[:7]} → 远端 {remote[:7]}")
                info = fetch_release_and_commits(r["path"], gh, branch)
                updates.append({
                    "repo": r,
                    "info": info,
                    "local": local,
                    "remote": remote,
                    "remote_name": remote_name,
                    "branch": branch,
                    "gh": gh,
                })
            else:
                log(f"  {r['name']} ({gh} via {remote_name}/{branch}): 最新")
        except Exception as e:
            log(f"检查 {r['name']} 出错: {e}")
    return updates


def process_updates(updates, oneshot=False, headless=False):
    """对每个更新征求同意并自动 pull (用自动识别的 remote + branch).
    发现多个更新时先弹一条汇总通知, 再逐个确认, 避免通知刷屏."""
    if updates:
        names = ", ".join(u["repo"]["name"] for u in updates[:5])
        more = f" 等 {len(updates)} 个" if len(updates) > 5 else ""
        notify(
            f"repo-watch: {len(updates)} 个项目有新版本",
            f"{names}{more} 发现更新。稍后将逐个弹窗确认 (点\"是\"才 git pull)。",
        )
    for u in updates:
        r = u["repo"]
        remote_name = u.get("remote_name", "origin")
        branch = u.get("branch", r["branch"])
        ok = confirm_update_interactive(r["name"], u["info"], headless=headless)
        if ok:
            do_pull(r["path"], r["name"], branch, remote_name)
        else:
            log(f"{r['name']} 用户选择暂不更新")
        time.sleep(1)


def main():
    # 读取本地配置 (setup.bat 写入的 Token 等)
    load_local_config()

    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="检查一次后退出")
    ap.add_argument("--list", action="store_true", help="仅列出发现的仓库")
    ap.add_argument("--no-token", action="store_true", help="不使用 GitHub Token (仅公开仓库)")
    ap.add_argument("--token", default=None, help="指定 GitHub Token")
    args = ap.parse_args()

    if args.no_token:
        CONFIG["github_token"] = ""
    if args.token:
        CONFIG["github_token"] = args.token

    log("=" * 60)
    log("repo-watch 启动 — 本机开源项目更新监控")
    log("=" * 60)

    if args.list:
        repos = discover_repos()
        for r in repos:
            up_mark = " [fork: upstream]" if r["upstream"] else ""
            src = r["upstream"] if r["upstream"] else r["origin"]
            print(f"  {r['name']:<30} {r.get('github') or src}  @ {r['branch']}{up_mark}")
        print(f"共 {len(repos)} 个仓库")
        return

    if args.once:
        repos = discover_repos()
        updates = check_repos(repos)
        if not updates:
            log("所有仓库均为最新, 无需更新。")
        else:
            process_updates(updates, oneshot=True, headless=False)
        return

    # 常驻模式: 开机 30 分钟后才开始, 之后每 30 分钟一次
    # 无控制台 (pythonw) = 后台静默; 有控制台 (python) = 前台, 可用终端确认
    headless = sys.stdin is None or sys.stdout is None
    first_delay = 30 * 60
    interval = CONFIG["interval_minutes"] * 60
    log(f"常驻模式: 首次扫描在 {first_delay//60} 分钟后, 之后每 {interval//60} 分钟一次 (headless={headless})")
    time.sleep(first_delay)
    while True:
        try:
            repos = discover_repos()
            updates = check_repos(repos)
            if updates:
                process_updates(updates, oneshot=False, headless=headless)
            else:
                log("本轮: 所有仓库均为最新")
        except KeyboardInterrupt:
            log("收到中断, 退出")
            break
        except Exception as e:
            log(f"本轮扫描出错: {e}")
        time.sleep(interval)


if __name__ == "__main__":
    main()

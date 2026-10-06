# repo-watch — 仓库哨兵（本机 Git 项目自动更新监控）

单文件、零维护的 Windows 后台监控工具：自动扫描所有盘符上的 Git 仓库，检测上游更新，发现后弹出 Windows 系统通知，确认后自动 `git pull`。

适用于：你电脑上散落的**开源项目 / 克隆 / fork**（不论是否属于你的 GitHub 账号）。工具会**智能判断**每个仓库该往哪拉：有 `upstream` remote 就拉上游原始项目，否则拉 `origin` 的默认分支。

## 特性

- 一条命令静默安装：`setup.bat` 无交互、无需管理员权限（可选传 Token）
- 自动扫描 C:/D:/E: 等所有固定盘，识别 Git 仓库
- 智能上游识别：自动判断 fork / 纯 clone / 自有项目，选对 pull 来源
- 自动探测 fork 上游的真实默认分支（GitHub API）
- 脏工作区（有未提交改动）自动**跳过并警告**，不污染本地
- 仅 Windows 系统通知（Toast），逐个弹窗确认后才自动 `git pull --ff-only`
- 后台常驻（pythonw 无窗口），开机自启（Startup VBS），首次延迟 30 分钟、之后每 30 分钟循环
- 后台模式下确认弹窗若不可用会**跳过而非卡死**，下一轮再试
- 仅依赖 `win10toast`，其余全为系统自带

## 快速开始

一条命令静默安装（可选传 GitHub Token，否则仅公开仓库）：

```bat
setup.bat ghp_xxx      :: 配 Token
setup.bat              :: 不配 Token（仅公开仓库）
```

装完即后台常驻，无需交互、无需管理员权限。之后：

- 任务管理器可看到 `pythonw repo_watch.py` 后台进程
- 开机登录自动启动（Startup 目录 `repo-watch.vbs`），**30 分钟后**首次扫描，之后每 30 分钟一次
- 有更新 → 右下角 Windows 通知 → 逐个弹窗确认（点"是"才 `git pull`）
- 没有更新时完全静默，不打扰

## 手动命令

```bat
python repo_watch.py                  :: 常驻后台（30 分钟后首次扫描）
python repo_watch.py --once           :: 立即检查一次后退出
python repo_watch.py --list           :: 仅列出发现的所有仓库
python repo_watch.py --token ghp_xxx  :: 指定 GitHub Token
python repo_watch.py --no-token       :: 禁用 Token（仅公开仓库）
```

## 配置

默认读 `repo_watch.config.json`（setup.bat 自动创建）。可手动编辑：

```json
{
  "github_token": "ghp_xxx",
  "interval_minutes": 30,
  "drives": null,
  "dirty_policy": "skip",
  "toast_display_len": 10
}
```

- `github_token`：私有仓库 + 更高 API 限流（留空 = 仅公开仓库）
- `interval_minutes`：常驻扫描间隔（分钟）
- `drives`：`null` = 自动检测全部固定盘；也可指定 `["C:\\", "D:\\"]`
- `dirty_policy`：`skip` = 脏工作区跳过并警告（当前唯一实现）
- `toast_display_len`：通知停留秒数

## 工作原理（智能上游识别）

对每个仓库：

1. 读 `git remote` → 同时拿 `origin` 和 `upstream`（若有）
2. 自动选择更新来源：
   - **有 `upstream`**（fork 场景）→ 拉 `upstream` 默认分支（上游原始项目最新），
     并用 GitHub API 探测上游真实默认分支名
   - **无 `upstream`**（纯 clone / 自有项目）→ 拉 `origin` 默认分支
3. 比对本地 HEAD 与所选 remote 的默认分支 HEAD（轻量 `git ls-remote`）
4. 若有更新 → 先弹一条汇总通知，再逐个弹窗确认 → `git pull --ff-only <remote> <branch>`
5. 脏工作区（`git status --porcelain` 非空）→ 跳过 + 警告
6. 后台（pythonw）模式下确认弹窗不可用时 → 跳过该仓库（下一轮再试），**绝不卡死**

## 自启动

- `setup.bat` 自动生成当前用户 Startup 目录下的 `repo-watch.vbs`
  （`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\repo-watch.vbs`），
  开机登录时静默拉起 `pythonw repo_watch.py`（无窗口、无交互、无需管理员）
- 脚本自身再延迟 30 分钟做首次扫描，之后每 30 分钟一次

## 卸载

```bat
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\repo-watch.vbs"   :: 移除开机自启
del repo_watch_state.json                                                      :: 清本地缓存
taskkill /f /im pythonw.exe                                                   :: 结束后台进程
```

（不想留依赖可再 `pip uninstall win10toast`。卸载前可先 `python repo_watch.py --once` 验证一轮。）

## 文件清单

| 文件 | 说明 |
|------|------|
| `repo_watch.py` | 主脚本（单文件，全部逻辑） |
| `setup.bat` | 一条命令静默安装（自动把 VBS 写入 Startup，无需管理员） |
| `repo-watch.vbs` | 开机自启脚本，由 setup.bat 生成到 Startup 目录 |
| `requirements.txt` | 依赖（仅 win10toast） |
| `.gitignore` | 忽略运行时生成文件 |
| `repo_watch_state.json` | 运行时自动生成的扫描缓存 |
| `repo_watch.config.json` | 运行时自动生成的配置（Token） |

## 注意

- 首次全盘扫描可能较慢（几百仓库），之后走缓存更快
- 系统通知需要 Windows 允许"应用"通知；若收不到，到 设置 → 通知 里允许
- 脚本以 `pythonw`（无窗口）后台运行；想看日志可用 `python repo_watch.py` 前台跑
- 批量更新 / 推送请用 Git 本身或 CI；本工具只做"发现 + 通知 + 确认后 pull"

---
---

# English Reference (repo-watch)

A single-file, zero-maintenance **Windows background monitor** for Git repositories. It scans every fixed drive for Git repos, checks whether the default branch is behind its upstream, and when an update is found, pops a **Windows system notification**. After your confirmation it runs `git pull --ff-only` automatically.

Use it for: any open-source projects / clones / forks scattered on your machine (whether or not they belong to your own GitHub account). The tool **intelligently picks** the right pull source: if the repo has an `upstream` remote it pulls from the original upstream project, otherwise it pulls `origin`'s default branch.

## Features

- One-command silent install: `setup.bat` is fully non-interactive and needs no admin
  (optionally pass a GitHub Token as the first argument)
- Scans C:/D:/E: (all fixed drives) and detects Git repositories
- Smart upstream detection: fork / plain clone / own project → correct pull source
- Auto-detects the upstream's real default branch via the GitHub API
- Dirty worktrees (uncommitted changes) are **skipped with a warning** — your local work is never touched
- Windows toast notifications only; each update is confirmed per-repo before `git pull --ff-only`
- Resident background process (`pythonw`, no window); autostart via a Startup VBS that setup.bat
  writes into the user's Startup folder; first scan after 30 min, then every 30 min
- In the background (pythonw) mode, if the confirm dialog is unavailable the repo is
  **skipped (retried next round) instead of hanging**
- Single dependency: `win10toast`; everything else is built into Windows

## Quick start

One-command silent install (optionally pass a GitHub Token, otherwise public repos only):

```bat
setup.bat ghp_xxx      :: with Token
setup.bat              :: without Token (public repos only)
```

Once installed it stays resident in the background with no interaction and no admin. Afterwards:

- Task Manager shows a `pythonw repo_watch.py` background process
- Autostarts on logon (Startup `repo-watch.vbs`); **first scan after 30 minutes**, then every 30 min
- Update found → Windows notification at bottom-right → per-repo confirm dialog (click "Yes" to `git pull`)
- Completely silent when there is nothing to update

## Manual commands

```bat
python repo_watch.py                  :: resident mode (first scan after 30 min)
python repo_watch.py --once           :: check once, then exit
python repo_watch.py --list           :: just list discovered repos
python repo_watch.py --token ghp_xxx  :: supply a GitHub token
python repo_watch.py --no-token       :: disable token (public repos only)
```

## Configuration

Reads `repo_watch.config.json` (created by setup.bat). Edit manually:

```json
{
  "github_token": "ghp_xxx",
  "interval_minutes": 30,
  "drives": null,
  "dirty_policy": "skip",
  "toast_display_len": 10
}
```

- `github_token` — private repos + higher API rate limit (empty = public only)
- `interval_minutes` — resident scan interval (minutes)
- `drives` — `null` = auto-detect all fixed drives; or e.g. `["C:\\", "D:\\"]`
- `dirty_policy` — `skip` = skip dirty worktrees with a warning (current implementation)
- `toast_display_len` — notification display duration in seconds

## How it works (smart upstream detection)

For each repo:

1. Read `git remote` → capture `origin` and `upstream` (if present)
2. Pick the update source:
   - **Has `upstream`** (fork scenario) → pull `upstream`'s default branch (the original project),
     detecting the real default-branch name via the GitHub API
   - **No `upstream`** (plain clone / own project) → pull `origin`'s default branch
3. Compare local HEAD against the chosen remote's default-branch HEAD (lightweight `git ls-remote`)
4. Update available → one summary toast, then per-repo confirm dialog → `git pull --ff-only <remote> <branch>`
5. Dirty worktree (`git status --porcelain` non-empty) → skip + warn
6. In background (pythonw) mode, if the confirm dialog is unavailable → skip that repo
   (retried next round) instead of hanging

## Autostart

- `setup.bat` writes `repo-watch.vbs` into the current user's Startup folder
  (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\repo-watch.vbs`);
  on logon it silently launches `pythonw repo_watch.py` (no window, no interaction, no admin)
- The script itself delays 30 minutes before the first scan, then runs every 30 minutes

## Uninstall

```bat
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\repo-watch.vbs"   :: remove autostart
del repo_watch_state.json                                                      :: clear cache
taskkill /f /im pythonw.exe                                                   :: end the background process
```

(Optionally `pip uninstall win10toast` to drop the dependency. Before uninstalling you can run
`python repo_watch.py --once` to verify one pass.)

## File layout

| File | Description |
|------|------|
| `repo_watch.py` | Main script (single file, all logic) |
| `setup.bat` | One-command silent installer (writes the VBS to Startup, no admin needed) |
| `repo-watch.vbs` | Autostart script, generated by setup.bat into the Startup folder |
| `requirements.txt` | Dependencies (win10toast only) |
| `.gitignore` | Ignores runtime-generated files |
| `repo_watch_state.json` | Scan cache, auto-generated at runtime |
| `repo_watch.config.json` | Config (Token), auto-generated at runtime |

## Notes

- The first full-drive scan can be slow (hundreds of repos); subsequent scans use the cache
- Windows must allow "app" notifications; if toasts don't appear, enable them in Settings → Notifications
- The script runs as `pythonw` (no window); run `python repo_watch.py` in the foreground to see logs
- For batch update/push use Git itself or CI — this tool only does "detect + notify + pull-on-confirm"

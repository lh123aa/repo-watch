# 我懒得手动 git pull，所以写了一个 574 行的后台守护

> build-in-public · L4 案例资产 #1 · 发布渠道：知乎 / 即刻 / X
> 预计字数：~1200 字（短文） · 预计阅读：4 分钟

---

## 起点：一个很小的烦

我本地同时维护着 5 个 git 仓库，分散在 `E:\程序\github\` 和 `E:\程序\我的项目\`。

以前每次开工前要"巡一遍"：

```
cd 仓库A && git pull
cd 仓库B && git pull
...
```

5 个仓库，每个 30 秒，一天巡 3 次 = 15 分钟纯机械劳动，而且很容易漏。

更烦的是：**有 dirty working tree 的仓库**——你忘了 stash 就 pull，会报错。要么手动 `stash → pull → pop`，要么干脆跳过那个仓库，结果下次打开发现落后 8 个 commit。

## 解法：后台守护 + toast 通知

写了一个 `repo_watch.py`，574 行 Python，零 GUI 依赖：

1. **30 分钟一轮**：扫所有本地 git 仓库
2. **对比远端**：每个仓库做一次 `git fetch --dry-run`（或 `ls-remote` 对比 `HEAD` 和 `origin/HEAD`）
3. **有更新就弹 toast**：Windows 系统通知（`win10toast`），标题是仓库名，内容是 `+N commits`
4. **点 toast 就 pull**：脏工作区自动 `stash → pull → stash pop`
5. **开机自启**：VBS 脚本挂 Startup，重启后 `pythonw` 后台拉起来，不弹窗口

整个过程不需要人守着。我写代码、开会、吃饭，回来发现后台已经拉了 3 次，toast 还在通知栏里堆着。

## 技术细节（4 个关键点）

**① 不污染 PATH，不装全局**
`setup.bat` 4 步幂等：`pip install win10toast` → 写 `.token`（如果有 PAT）→ 生成 VBS → `pythonw repo_watch.py`。全部在仓库根目录完成，不影响系统。

**② dirty tree 安全**
```
git stash -u → git pull → git stash pop
```
每 30 分钟做一次，即使你的工作区有未提交改动也不会卡住。

**③ 基线记录，不重扫**
`repo_watch_state.json` 存每个仓库的上次 `HEAD` commit hash。重启后不需要重新扫全仓库，只看增量。

**④ 限流友好**
匿名调 GitHub API 只有 60 次/小时，5 个仓库每 30 分钟 2 次 fetch = 10 次/小时，远远够用。如果有 PAT，可以换成 5000 次/小时。

## 开源了

仓库在 GitHub：**[lh123aa/repo-watch](https://github.com/lh123aa/repo-watch)**

- 574 行，Python 3.8+
- 依赖只有 `win10toast`（Windows-only）
- 一行命令安装：`setup.bat`
- 完整项目背景见 `project-journal/`

## 为什么做这个？

不是为了卖，是为了验证一件事：**我能不能把"我懒得手动做"长出来一个小工具，做到可以给别人用？**

答案是 574 行代码 + 一个 30 分钟后台守护 + 一条开机自启 VBS，从 0 到开源 18 小时。

如果你也是 Windows 上同时维护 5+ 个本地仓库，clone 一下试试。如果你用 Linux/macOS，这版不支持——但我有想法，见文末。

---

**P.S.** 这是我"四层变现模型"的第一块拼图（L1 免费开源 → 验证需求 → 决定 L2/L3/L4 怎么走）。如果你关注我的 GitHub，可以订阅 `lh123aa/repo-watch`，看看 30 天后能不能做出东西。

---
*发布记录：2026-10-10 · 渠道：知乎 / 即刻 / X（三平台同发）· 定位：L4 案例资产 #1，不等 S2，当下就能做*

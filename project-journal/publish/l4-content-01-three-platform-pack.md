# L4 #1 三平台发布包（知乎 / 即刻 / X）

> 源文件：`l4-content-01-repo-watch-build-in-public.md`（~1200 字，完整叙事）
> 三平台各一份直接可粘贴的适配版 + 封面图清单 + 发布 checklist

---

## ① 知乎（长文 · 完整叙事）

**标题**：我懒得手动 git pull，所以写了一个 574 行的后台守护

**标签**（知乎选 2-3 个）：编程 / 程序员 / 效率工具 / Python / GitHub

**正文**（直接粘贴，全量 1200 字版，知乎支持 Markdown）：

---

我本地同时维护着 5 个 git 仓库，分散在 `E:\程序\github\` 和 `E:\程序\我的项目\`。

以前每次开工前要"巡一遍"：

```
cd 仓库A && git pull
cd 仓库B && git pull
...
```

5 个仓库，每个 30 秒，一天巡 3 次 = 15 分钟纯机械劳动，而且很容易漏。

更烦的是：**有 dirty working tree 的仓库**——你忘了 stash 就 pull，会报错。要么手动 `stash → pull → pop`，要么干脆跳过那个仓库，结果下次打开发现落后 8 个 commit。

### 解法：后台守护 + toast 通知

写了一个 `repo_watch.py`，574 行 Python，零 GUI 依赖：

1. **30 分钟一轮**：扫所有本地 git 仓库
2. **对比远端**：每个仓库做一次 `git fetch --dry-run`（或 `ls-remote` 对比 `HEAD` 和 `origin/HEAD`）
3. **有更新就弹 toast**：Windows 系统通知（`win10toast`），标题是仓库名，内容是 `+N commits`
4. **点 toast 就 pull**：脏工作区自动 `stash → pull → stash pop`
5. **开机自启**：VBS 脚本挂 Startup，重启后 `pythonw` 后台拉起来，不弹窗口

整个过程不需要人守着。我写代码、开会、吃饭，回来发现后台已经拉了 3 次，toast 还在通知栏里堆着。

### 4 个技术关键点（可照抄）

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

### 开源了

仓库在 GitHub：**[lh123aa/repo-watch](https://github.com/lh123aa/repo-watch)**

- 574 行，Python 3.8+
- 依赖只有 `win10toast`（Windows-only）
- 一行命令安装：`setup.bat`
- 完整项目背景见 `project-journal/`

### 为什么做这个？

不是为了卖，是为了验证一件事：**我能不能把"我懒得手动做"长出来一个小工具，做到可以给别人用？**

答案是 574 行代码 + 一个 30 分钟后台守护 + 一条开机自启 VBS，从 0 到开源 18 小时。

如果你也是 Windows 上同时维护 5+ 个本地仓库，clone 一下试试。如果你用 Linux/macOS，这版不支持——但我有想法。

---

*发布记录：2026-10-10 · L4 案例资产 #1，不等 S2，当下就做。*

---

**知乎发布步骤**：
1. 知乎 → 创建文章 → 标题粘贴 → 正文粘贴（选"导入"或"粘贴文本"）
2. 标签选 2-3 个（编程 / 程序员 / 效率工具 / Python / GitHub）
3. 封面：知乎支持上传封面图，选 `cover.png`（清单见下方）
4. 发布 → 把 URL 回填到 journal（见下方 checklist）

---

## ② 即刻（短 + 强观点 · 300 字以内）

**标题**（即刻标题 30 字以内）：懒得手动 git pull，写了个 574 行的后台守护

**正文**（即刻 1000 字以内，300 字最优）：

我本地同时维护 5 个 git 仓库，以前每次开工要巡一遍 `git pull`，一天 3 次 = 15 分钟纯机械劳动，还容易漏 dirty tree。

写了个 `repo_watch.py`（574 行 Python，零 GUI 依赖）：

- 30 分钟扫一轮
- 有更新弹 Windows toast（`win10toast`）
- 点 toast 自动 `stash → pull → stash pop`（dirty tree 安全）
- VBS 挂 Startup 开机自启，`pythonw` 后台跑，不弹窗口
- `repo_watch_state.json` 记基线，重启不重扫
- 一行命令安装：`setup.bat`

从 0 到开源 18 小时。不是为了卖，是验证"我能不能把懒出来的工具做到给别人用"。

仓库：github.com/lh123aa/repo-watch（Windows-only，574 行，Python 3.8+）

#程序员日常 #效率工具 #开源

---

**即刻发布步骤**：
1. 即刻 → 发即刻 → 粘贴正文（话题标签直接打在正文里，即刻不支持独立标签位）
2. 可附 1-4 张图：`cover.png`（清单见下）
3. 发布 → 把 URL 回填到 journal

---

## ③ X（英文 · 强 hook · 280 字符以内 + 线程可选）

**推文（单条，280 字符内）**：

Wrote a 574-line Python daemon that auto-`git pull`s every local repo every 30 min, pops a Windows toast, handles dirty trees with `stash → pull → stash pop`, and boots with the PC. Zero GUI.

It was just me hating the ritual of `cd repoA && git pull` ×5, three times a day.

Now it runs in the background. I forget it exists.

Windows-only, Python 3.8+, one `setup.bat` to install.

→ github.com/lh123aa/repo-watch

**可选线程（2 条，每条 280 字符内）**：

> **2/4** — 4 key design choices (steal these):
>
> ① No PATH pollution: `setup.bat` does `pip install win10toast` → write `.token` → generate VBS → `pythonw`. All in-repo, doesn't touch your system.
>
> ② Dirty-tree safe: every cycle does `git stash -u → git pull → git stash pop`. Your uncommitted work can't get stuck.
>
> ③ Baseline file (`repo_watch_state.json`) stores last-seen `HEAD` per repo. Restart = no full re-scan.
>
> ④ Rate-limit friendly: 5 repos × 2 fetches/hr = 10/hr. Anonymous GitHub API = 60/hr, no problem. PAT = 5000/hr if you need it.

> **3/3** — Why build this at all?
>
> Not to sell it. To validate a question: *can I turn "I'm lazy about X" into a tool someone else actually wants?*
>
> 574 lines + one 30-min background loop + one VBS auto-start = 18 hours from 0 to open source.
>
> If you're on Windows maintaining 5+ local repos, clone it and try. Linux/macOS: not supported yet — I have ideas (L2 SaaS, coming).
>
> I'll post 30 days of star/clone data back in November.

---

**X 发布步骤**：
1. X → New post → 粘贴主推文（1/3）
2. 附加图片：`cover.png`（清单见下）
3. 发布 → 把 URL 回填到 journal
4. 线程 2/4、3/3 作为后续两条发（间隔 30 秒以上，避免被限流）

---

## 封面图清单（三平台通用）

每张 `cover-*.png` 建议 1600×900（16:9），生成后统一放 `project-journal/publish/assets/`：

| 文件 | 内容 | 用于 |
|------|------|------|
| `cover-zhihu.png` | 黑底白字："574 行 Python 守护你的 5 个 git 仓库" + 副标题 "30 分钟一轮 · 自动 pull · 开机自启" + 仓库名 `lh123aa/repo-watch` | 知乎文章封面 |
| `cover-jike.png` | 白底黑字，同文案，加 GitHub star 图标 + "clone 试试" | 即刻附图 1 |
| `cover-x.png` | 深灰底 + 终端窗口截图（`pythonw repo_watch.py` 跑起来的一帧），底部加一行 "github.com/lh123aa/repo-watch" | X 推文配图 |
| `cover-screenshot.png` | 截一张 Windows 通知栏 toast 弹出来的真实画面（`repo-watch` 应用发一条测试 toast），标注 "你后台拉代码时，它长这样" | 三平台都可作附图 |

> **生成方式**：可以用 `gpt-image-2` skill 出 3 张封面（给 prompt 就行），`cover-screenshot.png` 你自己截图（或跑一次 `repo_watch.py` 看 toast 效果截下来）。
> **如果不想出图**：三平台都能先发文字版，封面后补，不影响首发时间。

---

## 发布 checklist（发完勾掉）

- [ ] 知乎：粘贴长文 + 选 2-3 标签 + 上传 `cover-zhihu.png` → 发布 → URL：______
- [ ] 即刻：粘贴 300 字版 + 话题标签（正文里打）+ 附 `cover-jike.png` → 发布 → URL：______
- [ ] X：粘贴英文主推文 + 附 `cover-x.png` → 发布 → URL：______（线程 2/4、3/3 作为后续两条发）
- [ ] 截一张 `cover-screenshot.png`（Windows 通知栏 toast 实拍）→ 三平台补图
- [ ] 把 3 个 URL 回填到 `journal/2026-10-10.md` 的 [T] L4 #1 条目 + 记 [M] l4_01_publish_time
- [ ] 跑 `journal.py index` + `lint` + `git add project-journal/ && git commit -m "L4 #1: publish URLs + metrics" && git push`

---

## 首发后 24h 数据回收（可选）

发完 24h 后，把各平台的"赞/评论/收藏/转发"数回填到 `metrics.csv`，作为 L4 副线的第一条数据点（非 S2 阻塞，纯参考）：

| 平台 | 赞 | 评论 | 收藏 | 转发 | 发布时间 |
|------|----|------|------|------|----------|
| 知乎 | ? | ? | ? | ? | 2026-10-11 |
| 即刻 | ? | ? | ? | ? | 2026-10-11 |
| X | ? | ? | ? | ? | 2026-10-11 |

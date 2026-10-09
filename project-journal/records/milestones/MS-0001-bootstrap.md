---
id: MS-0001
type: milestone
date: 2026-10-09
title: 项目骨架 + 自启部署完成, VBS 已拉起常驻
tags: [milestone, S1, deploy]
status: closed
---

# MS-0001 项目骨架 + 自启部署完成

## 事实
- 项目根 `E:\程序\github\repo-watch` 完整 7 文件骨架:
  - `repo_watch.py`(574 行 headless 守护, 30 分钟循环 + toast + git pull + stash 闭环)
  - `setup.bat`(GBK, 4 步幂等: 装依赖→写 token→生成 VBS→后台拉 `pythonw`)
  - `_gen_vbs.py`(GBK VBS 生成器)
  - `setup_token.py`(写 `repo_watch.config.json`)
  - `requirements.txt`(`win10toast`)
  - `README.md`(中文说明 + 英文附录)
  - `.gitignore`(排除 `repo_watch_state.json`、`repo_watch.config.json`、`__pycache__/`、`*.pyc`、`KNOWN_ISSUES.md`)
- 自启部署:
  - `C:\Users\49046\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\repo-watch.vbs` 已就位(GBK, 末尾反斜杠已剥)
  - VBS 内容: `WshShell.CurrentDirectory = "E:\程序\github\repo-watch"` + `WshShell.Run "pythonw ""E:\程序\github\repo-watch\repo_watch.py"", 0, False`
- 已推 GitHub 公开仓库 `lh123aa/repo-watch` `main` 分支, commit `2f6b56a`(7 文件)。
- 当前运行时: `pythonw` 双进程常驻(launcher + worker, 见 I-001/I-003)。
- 已生成 `KNOWN_ISSUES.md`(25 条, 现象/根因/状态/迭代方向 四段式 + P0–P3 优先级 + 回归检查清单)。

## 判断
- 项目已从"想法"进入 **S1 已部署/跑通**(自启 + 常驻 + 远端推送), 阶段该从 S0 推进到 S1。
- 自用 14 天时钟(成功线)从 2026-10-09 开始累计。

## 下一步
- 进入 14 天观察期, 每日检查: 进程存活、`repo_watch_state.json` 是否更新、toast 是否出现、pull 是否成功。

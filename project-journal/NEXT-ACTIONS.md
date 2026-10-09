# NEXT-ACTIONS . 未完成事项

> 手工维护（脚本不会覆盖本文件）。`STATE.md` 会自动引用这里的未勾选项。
> 规则：只保留"下一步真的要做的"；已完成的勾掉或删除；空的分区保留标题即可，不要留空 checkbox。

## 进行中（按优先级）
- [ ] 用户手动建 GitHub release v1.0.0(浏览器 Releases 页 1 次点击, 见下方"30 秒操作指引")
- [ ] 设 30 天到期(2026-11-08)数据回收提醒: star/clone/fork 对照成功线
- [ ] 安全卫生: 去 GitHub Settings → Developer settings → Personal access tokens, 确认旧 `ghp_V74X...` 已吊销(已 401 即视为失效)

### 30 秒手动建 release(用户侧)
1. 浏览器打开 https://github.com/lh123aa/repo-watch/releases
2. 点 "Draft a new release"
3. tag 选 `v1.0.0`, title 填 `v1.0.0 - 仓库哨兵`
4. body 粘贴 `release-notes-v100.md` 内容(或留空, tag message 已含摘要)
5. 点 "Publish release"
→ 完成后仓库会有 release 页 + 自动 zip/tar 下载 + assets

## 等待中（被外部阻塞）
- 30 天 S2 数据(截止 2026-11-08): star / clone / fork / issue, 决定进 S3 还是停推广

## 已完成（本周期，保留 2 周便于复盘）
- [x] 2026-10-09 建立项目记录目录
- [x] 2026-10-09 补全 CHARTER.md 成功线/止损线
- [x] 2026-10-09 项目骨架 + 自启部署 + 推 GitHub `lh123aa/repo-watch` (commit 2f6b56a)
- [x] 2026-10-09 KNOWN_ISSUES.md 25 条 + 加进 .gitignore
- [x] 2026-10-09 决策: 跳过 S1 观察期直接进 S2 (ADR-0001)
- [x] 2026-10-09 plugin 化定位: 获客漏斗而非主收入 (INS-0001)

## 想法池（尚未决定要不要做）
- 桌面 GUI 包装版(付费 $5–15 一次性)—— CHARTER §3 变现假设, 先用开源线验证需求再决定
- 跨平台(Linux/macOS)—— CHARTER §7 明确不做, 除非开源线突破
- **`project-journal` 脱敏成社区版 Agent 插件(DeepSeek/ClawHub)**—— 当获客漏斗, 不阻塞 S2; 30 天安装 < 20 即停(见 INS-0001)
- **托管版 SaaS($5–10/月订阅)**—— 等 plugin 安装数 > 100 再启动

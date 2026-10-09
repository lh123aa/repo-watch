# NEXT-ACTIONS . 未完成事项

> 手工维护（脚本不会覆盖本文件）。`STATE.md` 会自动引用这里的未勾选项。
> 规则：只保留"下一步真的要做的"；已完成的勾掉或删除；空的分区保留标题即可，不要留空 checkbox。

## 进行中（按优先级）
- [ ] 用户手动建 GitHub release v1.0.0(浏览器 Releases 页 1 次点击, 见下方"30 秒操作指引")
- [ ] 安全卫生: 去 GitHub Settings → Developer settings → Personal access tokens, 确认旧 `ghp_V74X...` 已吊销(已 401 即视为失效)
- [ ] **L4 案例+内容资产: 当下就能做, 不等 S2**: 3–5 篇 build-in-public 短文(知乎/即刻/X) + S2 到期后 3000 字案例 + 脱敏资产包(见 IN-0002)

### 30 秒手动建 release(用户侧)
1. 浏览器打开 https://github.com/lh123aa/repo-watch/releases/new
2. tag 选 `v1.0.0`(下拉里已有)
3. title 填 `v1.0.0 - 仓库哨兵 · 首个公开 release`
4. 点 "Publish release"(不是 Save as draft)
→ 完成后 `.github/workflows/release.yml` 自动挂 zip asset(3cb61ab 已推)

## 等待中（被外部阻塞）
- 30 天 S2 数据(截止 2026-11-08, 已设提醒): star / clone / fork / issue
  → 对照 IN-0002 决策树: 达标进 L2 托管 SaaS MVP; 不达标止损 L1+L2, 只留 L4 案例资产
- 2026-11-08 数据回收由 schedule-7ef7484b 自动触发

## 已完成（本周期，保留 2 周便于复盘）
- [x] 2026-10-09 建立项目记录目录
- [x] 2026-10-09 补全 CHARTER.md 成功线/止损线
- [x] 2026-10-09 项目骨架 + 自启部署 + 推 GitHub `lh123aa/repo-watch` (commit 2f6b56a)
- [x] 2026-10-09 决策: 跳过 S1 观察期直接进 S2 (ADR-0001)
- [x] 2026-10-09 plugin 化定位: 获客漏斗而非主收入 (INS-0001)
- [x] 2026-10-09 KNOWN_ISSUES.md 25 条 + 加进 .gitignore
- [x] 2026-10-09 变现四层模型 L1/L2/L3/L4 + S2 决策树 (IN-0002)
- [x] 2026-10-09 30 天数据回收提醒已设 (schedule-7ef7484b, 2026-11-08 09:00 Asia/Qatar)
- [x] 2026-10-09 release 自动挂 zip 的 workflow 已推 (commit 3cb61ab, .github/workflows/release.yml)

## 想法池（尚未决定要不要做）
- 桌面 GUI 包装版(付费 $5–15 一次性)—— CHARTER §3 变现假设, 先用开源线验证需求再决定
- 跨平台(Linux/macOS) —— **L2 托管 SaaS 默认含, 不再单独开分支** (IN-0002)
- **`project-journal` 脱敏成社区版 Agent 插件(DeepSeek/ClawHub)** —— 当获客漏斗, 不阻塞 S2; 30 天安装 < 20 即停(见 INS-0001)
- **托管版 SaaS($5–10/月订阅)** —— L2, 触发条件: S2 到期 star≥50 或 30 天安装≥100 且≥10 人 ask 跨平台 (IN-0002 决策树)

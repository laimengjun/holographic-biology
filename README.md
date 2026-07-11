# 全息生物 / Holographic Biology 研究项目

> **创建日期**: 2026-06-30
> **最后更新**: 2026-07-03 07:30
> **状态**: 🟢 主方向锁定 + 5.x/6.x/7.x 全部完成 + PDF 100+ 页 + 30 集课程 + 飞书推送
> **目标**: 围绕中文语境"全息生物"的主流含义（张颖清生物全息律）建立可迭代、可追溯的研究档案库

---

## 🎯 主方向：F. 张颖清"全息生物学"

**核心命题**（一段话）：
> 生物体每一相对独立的部分（耳、第二掌骨、足底等）是整体成比例的缩小，包含整体各部位的全部信息；通过刺激这些"全息胚"上对应的位点，可以诊断和治疗整体对应部位的疾病。

**关键人物**:
- 张颖清（**1947-2004**）— 山东大学全息生物学研究所，**理论奠基**
- 张秀勤（2006）— **现代中医临床应用中介**
- 韦三立 — 北京农大，**形式本体论延续**
- 杜长华 — 上海宝山中医医院，**临床应用**
- 邹承鲁（已故）— 中科院院士，**主流反对派**
- 王德奎 — 学派**内部反思者**

**已收文献**（`sourcing/`）:
- F-01 张颖清亲笔英文学术论战文章（7 页）
- F-02 韦三立/王德奎"形式本体论"（5 页）
- F-03 北京中医药大学全息刮痧临床报告（5 页）
- F-04 香港健康杂志 Page 13 英文科普（提取）

详细 Scope Note: `technical/F-zhang-yingqing-holographic-biology/scope-note.md`

## 📁 目录结构（截至 2026-07-03 07:30）

```
D:\obsidian\Holographic-Biology\
├── README.md                          ← 本文件
├── 工作计划.md                         ← 项目中枢
├── sourcing/                          ← 原始 PDF
├── technical/
│   ├── 00-方向澄清/方向澄清.md
│   └── F-zhang-yingqing-holographic-biology/  ★ 主方向
│       ├── scope-note.md              ← 11.5KB
│       ├── concept-map.md             ← 6 张 Mermaid 图
│       ├── review-draft.md            ← 综述 v2 (30.8KB / 5300 字 / 5 图嵌入)
│       ├── notes/                     ← 4 篇阅读笔记
│       ├── raw/                       ← 4 篇 PDF 转换的 MD
│       ├── 5.1-eeg-brain-computer-interface.md    ← 5.x 系列 (3 篇)
│       ├── 5.2-tongue-diagnosis-principles.md
│       ├── 5.3-pulse-diagnosis-tcm.md
│       ├── 6.1-dna-holographic-biology.md        ← 6.x 系列 (6 篇)
│       ├── 6.2-shannon-information-hologram.md
│       ├── 6.3-neural-segment-micro-system.md
│       ├── 6.4-holoscan-2-physics-implementation.md
│       ├── 6.5-mutation-holographic-embryo.md
│       └── 6.6-organoid-holographic-embryo.md
└── business-plan/                     ← ★ 应用转化
    ├── 科普文章-张颖清全息生物学30年.md
    ├── 4.2-commercial-idea.md         ← HoloScan 商业
    ├── 4.3-agent-metaphor.md          ← AI Agent 隐喻
    ├── 4.3-prototype-summary.md
    ├── HAIS-v0.1.md                   ← Agent 接口标准
    ├── holo_agent_prototype.py        ← 200 行原型
    ├── holo_agent_v0.2.py             ← 500 行 v0.2.6
    ├── holo_agent_v0.2_summary.md
    ├── 4.4-course-materials.md        ← 32 学时课件
    ├── 4.5-30-ep-short-video-course.md            ← 30 集课程设计
    ├── 4.5.1-30-ep-scripts.md         ← 30 集完整脚本 (69KB)
    ├── 4.5.2-video-prompts.md         ← 30 集视频提示词
    ├── 4.5.3-narration.md             ← 30 集旁白稿
    ├── 4.5.5-split-script.py          ← 脚本拆分工具
    ├── 4.5.6-cosyvoice-batch.py       ← CosyVoice 批量 TTS
    ├── 5.0-knowledge-expansion-summary.md          ← 5.x summary
    ├── 6.0-physics-foundations-summary.md          ← 6.x summary (完整版)
    ├── 7.0-tcm-holography-overview.md              ← 7.x 总览 + 知识图谱 🆕
    ├── 7.1-tcm-natural-therapies-mapping.md        ← 63 种疗法映射 🆕
    ├── 7.2-modern-medicine-holography.md           ← 现代医学全息现象 🆕
    ├── 7.3-cross-cultural-comparison.md            ← 跨文化传统医学对照 🆕
    ├── 7.4-frontier-directions.md                  ← 6 大前沿方向 🆕
    ├── 7.5-ai-agent-holography.md                  ← AI Agent 全息架构 🆕
    ├── 7.x-application-expansion-summary.md        ← 7.x 系列总结 🆕
    ├── generate_pdf.py                ← Edge headless → PDF
    └── business-plan-book.pdf         ← 100+ 页 / 5.05 MB
```

## 📊 项目统计（截至 2026-07-03 07:30）

| 维度 | 数量 |
|------|------|
| MD 文档 | **44+** 份 |
| 总字数 | **~17 万字** |
| Mermaid 图 | 7 张 |
| Python 代码 | 5 份 |
| PDF | 100+ 页 / 5.05 MB |
| 30 集课程 | ✅ 完整脚本 + 旁白 |
| 飞书推送 | ✅ 3 条消息 |
| 7.x 应用扩展 | ✅ 6 篇完成 |

## 🔀 方向对照

| 方向 | 状态 | 与 F 关系 |
|------|------|----------|
| **F 张颖清** | 🟢 主方向 | — |
| A Holobiont | 🟡 辅助 | "部分-整体"哲学相通 |
| E 分形生物体 | 🟡 辅助 | 自相似 / 标度律 |
| B / C / D | ⚪ 暂搁 | 同名异义，避免混淆 |

## 🔗 关联项目

- `D:\obsidian\Project-Solara\` — 哲学层面（"Liminal OS" ↔ "全息胚" 都谈"边界/涌现"）
- `D:\obsidian\teacher_welfare\` — 不冲突

## 🎯 Top 10 优先级（2026-07-03 07:30）

| # | 任务 | 状态 | 备注 |
|---|------|------|------|
| 1 | ✅ 综述 v2 | 完成 | 5 图嵌入，30.8KB |
| 2 | ✅ HoloAgent v0.2.6 | 完成 | 路径 A + 5 bug 修复 |
| 3 | ✅ 5.x 知识扩展 | 完成 | 3 篇 + summary |
| 4 | ✅ 6.x 物理学基础 | 完成 | 6 篇六位一体闭环 |
| 5 | ✅ 30 集课程 | 完成 | 设计 + 脚本 + 旁白 |
| 6 | ✅ PDF + 飞书推送 | 完成 | 100+ 页 / 5.05 MB / 3 条消息 |
| 7 | ✅ 7.x 应用扩展 | 完成 | 6 篇 26.5K 字 |
| **8** | 🔴 CNKI 手动 | 用户手动 | 10 篇核心论文（综述 v3 依赖） |
| **9** | 🟡 HAIS v0.2 | 2 周内 | 记忆隔离 + 跨 Agent 消息总线 |
| **10** | ⚪ HoloScan 2.0 MVP 立项 | 待决策 | ¥350 万 / 6 个月 |

详见 `工作计划.md`。

---

_本 README 在阶段 4 + 阶段 5 + 5.x + 6.x + 7.x 全部系列完成后再次更新。_
# Git 项目化准备方案 · `git-prepare.md`

> **创建日期**: 2026-07-06 08:55
> **状态**: ⏸️ 待用户拍板 5 个决策点后执行
> **目标**: 把 `D:\obsidian\Holographic-Biology\` 转为结构化、可维护、可分享的 git 项目
> **对应会话**: 2026-07-06 08:55 "把刚才的建议保存起来"

---

## ⚡ TL;DR — 等你一句话就开干

回我 **`按你的推荐开干 B+δ`** 我就一气呵成；或改其中几条。

**默认推荐组合**：策略 B（轻度整理） + 二进制方案 δ（最终版入库，过程 PDF 不入）

---

## 📋 项目现状（2026-07-06 摸底）

| 维度 | 数据 |
|---|---|
| 项目根 | `D:\obsidian\Holographic-Biology\` |
| 是否 Obsidian vault 子目录 | ❌ 否（无 `.obsidian/` / 无 `[[双链]]`） |
| MD 文件 | 92 份 |
| 总体积 | ~111 MB |
| 业务计划 PDF | ~30 个，约 45 MB |
| Python 代码 | 5 份（holo_agent / TTS / PDF / 脚本拆分） |
| git | ✅ 2.44.0 已装 / ❌ 全局 user 未配 / ❌ 无仓库 / SSH ed25519 已有 |
| 旧版本残留 | `business-plan-book - 0703.pdf` 已被 `business-plan-book.pdf` 取代；`test_unrestricted.md` 临时文件 |

---

## 🎯 三大战略决策

### 决策 1：策略 A / B / C

| 策略 | 工作量 | 风险 | 推荐 |
|---|---|---|---|
| **A. 最小侵入** | 30 分钟 | 几乎无 | ❌ 太糙 |
| **B. 轻度整理** ⭐ | 半天 | 低 | ✅ **推荐** |
| **C. 完全重构** | 1-2 天 | 中 | 长期主义但重 |

**B 做法**：A 的基础上 + 清理过时 PDF + 把内容分类归档，不大动结构

### 决策 2：二进制文件怎么管

| 方案 | 做法 | 仓库体积 |
|---|---|---|
| α | 全不入库 + 重建脚本 | < 1 MB |
| β | 全部入库 | ~50 MB |
| γ | Git LFS | ~2 MB + LFS 40 MB |
| **δ** ⭐ | **只入"最终版"** | ~10 MB |

**δ 做法**：
- `business-plan-book.pdf`（8.2 MB 最终版）✅ 入库
- `business-plan-book - 0703.pdf`（7.98 MB 旧版）❌ 删除
- vol1-8 单卷 PDF ❌ 排除（compendium-1000p-monograph.pdf 11.6 MB 单文件已包含）
- `generate_pdf.py` / `merge_pdfs.py` 生成的 PDF ❌ 排除
- 公众号 PDF、原始 PDF（`sourcing/`）✅ 入库（不可重建）

### 决策 3：版本节奏

**推荐**：`main` + tags + `drafts/` 子目录

里程碑 tag 节奏：
```
v0.1  2026-06-30  方向锁定 + 4 篇 PDF 阅读
v0.5  2026-07-01  综述初稿 + HoloAgent 原型
v1.0  2026-07-02  综述 v2 + 5.x 知识扩展 + 30 集课程
v1.5  2026-07-03  6.x 物理基础 + 7.x 应用扩展 + 1000 页专著
当前   HEAD      = v2.0-ready（待 git 化）
```

---

## 🏗️ 推荐目录结构（策略 B + 方案 δ）

```
D:\obsidian\Holographic-Biology\
├── .git/                                  ← 自动
├── .gitignore                              ← ⭐ 必备
├── .gitattributes                          ← Markdown diff 友好
├── README.md                               ← 重写为 git-homepage 风格
├── CHANGELOG.md                            ← 版本记录（v0.1 → 当前）
├── CITATION.cff                            ← 学术引用文件
├── LICENSE                                  ← CC-BY-4.0 推荐
├── git-prepare.md                          ← 本文件
├── docs/                                   ← 跨主题文档
│   ├── 00-roadmap.md                       ← 原 工作计划.md（精简）
│   ├── 01-scope-note.md                    ← 原 scope-note.md
│   ├── 02-concept-map.md                   ← 原 concept-map.md
│   ├── 03-review-draft.md                  ← 原 review-draft.md（综述）
│   ├── 04-directions.md                    ← 原 方向澄清.md
│   └── 05-stage-2-search-report.md
├── research/                               ← 学术研究系列
│   ├── foundations/                        ← 张颖清学派核心
│   │   ├── F-01-reading-note.md
│   │   ├── F-02-reading-note.md
│   │   ├── F-03-reading-note.md
│   │   ├── F-04-reading-note.md
│   │   ├── holographic-biology-zou-chenglu-dialogue.md
│   │   ├── holographic-meridian-scrapping-hypertension.md
│   │   ├── holographic-research-formal-ontology.md
│   │   └── biotech-magazine-page13-extract.md
│   ├── extensions/                         ← 5.x
│   │   ├── 5.1-eeg-brain-computer-interface.md
│   │   ├── 5.2-tongue-diagnosis-principles.md
│   │   ├── 5.3-pulse-diagnosis-tcm.md
│   │   └── 5.0-summary.md
│   ├── physics/                            ← 6.x
│   │   ├── 6.1-dna-holographic-biology.md
│   │   ├── 6.2-shannon-information-hologram.md
│   │   ├── 6.3-neural-segment-micro-system.md
│   │   ├── 6.4-holoscan-2-physics-implementation.md
│   │   ├── 6.5-mutation-holographic-embryo.md
│   │   ├── 6.6-organoid-holographic-embryo.md
│   │   └── 6.0-summary.md
│   └── applications/                       ← 7.x
│       ├── 7.0-tcm-holography-overview.md
│       ├── 7.1-tcm-natural-therapies-mapping.md
│       ├── 7.2-modern-medicine-holography.md
│       ├── 7.3-cross-cultural-comparison.md
│       ├── 7.4-frontier-directions.md
│       ├── 7.5-ai-agent-holography.md
│       └── 7.x-summary.md
├── product/                                ← 产品化成果
│   ├── hais/                               ← HoloAgent Interface Standard
│   │   ├── HAIS-v0.1.md
│   │   └── HAIS-v0.2-design.md
│   ├── holoagent/                          ← HoloAgent 多 agent 系统
│   │   ├── holo_agent_prototype.py         ← 200 行 v0.1
│   │   ├── holo_agent_v0.2.py              ← v0.2.6
│   │   └── holo_agent_v0.2_summary.md
│   ├── holoscan/                           ← HoloScan 2.0 商业项目
│   │   ├── 4.2-commercial-idea.md
│   │   ├── 8.1-holoscan-2.0-agency-plan.md
│   │   ├── 8.2-holoscan-2.0-project-charter.md
│   │   ├── 8.3-holoscan-2.0-detailed-wbs.md
│   │   ├── 8.4-holoscan-2.0-investor-bp.md
│   │   ├── 8.5-holoscan-2.0-team-recruitment.md
│   │   └── monograph/                      ← 1000 页专著章节 8.6-8.45
│   ├── course/                             ← 课程
│   │   ├── 4.4-course-materials.md
│   │   ├── 4.5-30-ep-short-video-course.md
│   │   ├── 4.5.1-scripts.md
│   │   ├── 4.5.2-video-prompts.md
│   │   └── 4.5.3-narration.md
│   └── popular-science/                    ← 科普
│       └── 科普文章-张颖清全息生物学30年.md
├── sources/                                ← 原始材料（不可重建）
│   ├── primary/                            ← 4 篇核心 PDF
│   │   ├── F-01-zhang-yingqing-english-debate.pdf
│   │   ├── F-02-wei-sanli-formal-ontology.pdf
│   │   ├── F-03-meridian-scrapping-case.pdf
│   │   ├── F-04-hongkong-magazine.pdf
│   │   └── 大脑分层结构.rtf
│   ├── related/                            ← 微信图片等
│   │   └── 微信图片_2026-06-30_114550_572.jpg
│   └── archive/                            ← 标注"未纳入主方向"
│       └── 生物技術研究新動態.pdf
├── scripts/                                ← 工具脚本
│   ├── README.md
│   ├── pdf/
│   │   ├── generate_pdf.py
│   │   ├── merge_pdfs.py
│   │   ├── generate_bp_pptx.py
│   │   ├── generate_pdfs_split.py
│   │   └── README.md
│   ├── tts/
│   │   ├── 4.5.5-split-script.py
│   │   ├── 4.5.6-cosyvoice-batch.py
│   │   └── README.md
│   └── agent/
│       └── README.md                       ← 如何跑 HoloAgent
├── papers/                                 ← 出版级 PDF（最终版）
│   ├── monograph-1000p.pdf                 ← 11.6 MB 唯一主版本
│   ├── business-plan-book.pdf              ← 8.2 MB 唯一主版本
│   └── vol1-8 单卷 → 不入库
├── drafts/                                 ← 在工作品
│   ├── 当前未发表内容/
│   └── README.md
└── assets/                                 ← 图片/图表
    └── (待补 Mermaid 导出的 SVG)
```

### 重命名规范（顺手统一）
- `holo_agent_v0.2.py` → `product/holoagent/v0.2.6.py`
- `4.5.1-30-ep-scripts.md` → `product/course/scripts-30ep.md`
- `8.x-monograph-volX-chY-*.md` → `product/holoscan/monograph/volX-chY-*.md`
- `增加.docx` → 转 md 入库或归档

---

## 📝 `.gitignore` 草案

```gitignore
# Obsidian / 系统
.obsidian/
.trash/
.DS_Store
Thumbs.db
*.tmp
*.bak
*~
~*

# Python
__pycache__/
*.pyc
*.pyo
.env
.venv/
venv/

# 二进制生成物（脚本可重建）
*.pdf
*.pptx
*.docx
*.wav
*.mp3
*.mp4
*.mkv
*.flac

# 特定忽略（已知旧版/临时文件）
test_unrestricted.md
business-plan-book - 0703.pdf

# 媒体层噪音（无关视频）
media/
```

---

## 🔨 我会做的 6 步（你 OK 就一气呵成）

1. **`git init`** + 全局配置 `user.name` / `user.email`（会问你）
2. **写 `.gitignore`** + `.gitattributes`
3. **第一次提交**（除新 PDF 外的全部内容）→ commit: `chore: 初始化全息生物学研究项目 git 仓库`
4. **改名规则化**（路径调整、统一命名）
5. **改写 README** 为 git 友好（不动学术内容）
6. **创建 CHANGELOG.md** 把 v0.1→v1.5 全填上

## ❌ 我**不会**自动做的事

- 删任何文件（除非是已知的旧版本如 `business-plan-book - 0703.pdf`，会先 dry-run 让你确认）
- 推送远程仓库（需要你提供 URL 或确认新建）
- 切换 LICENSE（会问）
- 改写正文（只动结构和元数据）

---

## ❓ 5 个待你拍板的事（默认推荐 OK 就发 `按你的推荐开干 B+δ`）

| # | 问题 | 我的默认推荐 |
|---|---|---|
| 1 | 选策略 A / B / C？ | **B**（轻度整理） |
| 2 | 选二进制方案 α/β/γ/δ？ | **δ**（最终版入库，过程 PDF 不入） |
| 3 | 当前目录建仓 vs 新建子目录？ | **当前目录** `D:\obsidian\Holographic-Biology\` 直接 init |
| 4 | LICENSE 选？ | **CC-BY-4.0**（学术知识库最佳实践） |
| 5 | 推送远程吗？配置在哪里？ | **先只本地**，远程留着你说 |
| 补充 | git `user.name` / `user.email`？ | **用你的真实姓名 + 一个邮箱（你给）** |

---

## 📜 待办（一旦启动后）

- [ ] 收集 git user.name / user.email
- [ ] 写 `.gitignore` 与 `.gitattributes`
- [ ] 第一次 commit（保留全部 md 与最终 PDF）
- [ ] 路径重构（按上面目录）
- [ ] 删除过时文件（dry-run 后）
- [ ] 改写 README.md 为 git 风格
- [ ] 写 CHANGELOG.md 与 CITATION.cff
- [ ] 补打 5 个 tag（v0.1 / v0.5 / v1.0 / v1.5 / v2.0）
- [ ] （可选）配远程 + push

---

_本文件是 2026-07-06 08:55 会话的"酝酿"快照。决策后我会移动到 `docs/06-git-prepare-history.md` 留作记录。_
# 企业财税分析 Skills 调研报告

> **日期**: 2026-07-02 16:30
> **目的**: 为"企业财税分析"任务找到最合适的 skills 组合
> **方法**: 
> 1. 扫描已安装 64 个 skills 的 SKILL.md
> 2. 搜索 skills.sh / ClawHub / GitHub 上的财税相关 skills
> 3. 按功能分类，标注可用性、风险、组合方案

---

## 一、企业财税分析的 5 大核心需求

| # | 需求 | 典型任务 |
|---|------|----------|
| 1 | **数据获取** | 抓上市公司财报/招股书/年报、税务政策、监管公告 |
| 2 | **数据存储与计算** | 财务比率、税务计算、行业基准、同业对比 |
| 3 | **数据可视化** | 趋势图、对比表、dashboard、PPT 报告 |
| 4 | **工作流自动化** | 定期抓取、月报生成、批量分析 |
| 5 | **协作与文档** | 飞书/Notion 报告、归档、合规留痕 |

---

## 二、已安装 skills 评估（直接可用）

### ⭐⭐⭐ 强烈推荐（财税核心组合）

| Skill | 功能 | 财税适用性 |
|-------|------|-----------|
| **data-visualization-2** | 图表生成（matplotlib/infsh） | 财务比率图、趋势图、行业对比表 |
| **database-operations** | SQL 优化/schema/索引 | 财务数据存储与查询 |
| **multi-search-engine** | 16 引擎搜索（无 API key） | 政策法规查询、公开信息抓取 |
| **tavily-search** | AI 优化搜索 | 快速获取 AI 整理过的财务/税务资料 |
| **perplexity** | AI 搜索 + 引用 | 政策解读、案例查询 |
| **web-search-exa** | 神经搜索 | 财报/招股书全文检索 |
| **scrapling** | 反爬网页抓取 | 抓上市公司公告、年报 PDF |
| **firecrawl-api / firecrawl-search** | 网页抓取（含 JS）| 抓动态网站财报 |
| **n8n / n8n-workflow-automation** | 工作流平台 | 月报自动化、定时抓取 |
| **documents** | 个人/企业文档管理 | 合同、税务文档归档 |
| **memos / usememos** | 快速笔记 | 财税分析洞察记录 |
| **obsidian-organizer** | 本地知识管理 | 政策法规 + 案例库 |

### ⭐⭐ 可用但需配置

| Skill | 现状 | 需配置 |
|-------|------|--------|
| **agent-reach** | 14 平台（含 RSS）| 抓公告/订阅源 |
| **blogwatcher** | RSS 监控 | 监控税务局/上市公司公告 |
| **feishu-* / notion** | 部分安装 | 报告协作 |
| **gitnexus** | 代码分析 | 公开代码 + 数据分析 |
| **composio** | 多 API 集成 | 接入金蝶/用友/QuickBooks |
| **gmail-oauth** | 邮件 OAuth | 邮件解析发票/账单 |
| **outlook-plus** | Outlook 集成 | 邮件附件发票 |
| **tavily-search** | ✓ | 已经在用 |
| **ai-automation-workflow** | AI 自动化（中英混合）| 适合国内业务流 |
| **war-room** | 多 Agent 协作 | 复杂财税方案设计 |

### ⭐ 不直接相关但有用

| Skill | 用法 |
|-------|------|
| **summarize** | 长文档摘要（财报/政策）|
| **self-improving** | 分析流程自我迭代 |
| **skill-vetter** | 安装新 skill 前必用 |
| **find-popular-skills** | 持续发现新 skills |

---

## 三、需补充的 skills（GitHub / ClawHub 找到）

### A. 财务/记账专用（推荐试用）

| Skill | 仓库 | ⭐ | 用途 | 风险 |
|-------|------|---|------|------|
| **moneywiz-ledger** | `eddieran/moneywiz-ledger` | 1 | 自然语言记账（个人/小微企业）| 🟢 低（小额记账） |
| **recite-agent-skill** | `rivradev/recite-agent-skill` | 2 | 收据扫描 + 自动归类 + CSV 输出 | 🟡 中（OCR 准确性）|
| **DocFlow-Presentations-and-Docs-Skill** | `rafalozan0/DocFlow-Presentations-and-Docs-Skill` | 3 | DOCX/XLSX/PDF/PPTX 一站式（替代 Documents）| 🟢 低（Hermes/OfficeSuite） |
| **OPENCLAW-SKILL-SAFE** | `cyrustmods/OPENCLAW-SKILL-SAFE` | 1 | 395 个安全 skills 的审计索引 | 🟢 低（参考用） |

### B. 专业财务/税务数据（需要付费 API）

| 资源 | 用途 | 接入方式 |
|------|------|----------|
| **Wind / 同花顺 iFinD / 东方财富 Choice** | 上市公司财报数据 | 需商业授权 |
| **天眼查 / 启信宝 / 企查查** | 企业工商/股东/对外投资 | 需 API key |
| **巨潮资讯网** | A 股年报/公告 | ✅ 公开，免费爬（推荐）|
| **港交所 HKEXnews** | 港股年报 | ✅ 公开，免费爬 |
| **美国 SEC EDGAR** | 美股 10-K/10-Q | ✅ 公开，免费爬 |
| **国家税务总局** | 中国税务法规 | ✅ 公开，免费爬 |
| **各地税务局官网** | 地方政策 | ✅ 公开，免费爬 |
| **裁判文书网** | 法律纠纷（影响税务）| ✅ 公开，免费爬 |

**结论**：**90% 财税数据可免费爬取**（用 multi-search-engine / firecrawl / scrapling），只有**深度结构化数据**（如财务比率自动计算）需付费。

---

## 四、推荐组合方案（按场景）

### 场景 1: 上市公司财报分析（A 股 / 港股 / 美股）

```
1. 数据获取
   ├─ multi-search-engine / tavily-search  → 找公司主页 / 公告
   ├─ scrapling + firecrawl-api            → 抓 PDF 年报/季报
   └─ agent-reach                          → 订阅公告 RSS

2. 文档处理
   ├─ nano-pdf                              → PDF 解析（提取财务表格）
   └─ summarize                             → 长文档摘要

3. 数据存储与计算
   ├─ database-operations                   → 财务数据库设计（建表）
   └─ Python (直接)                         → 财务比率计算 (ROE/ROA/资产负债率)

4. 可视化
   ├─ data-visualization-2                  → 趋势图、对比表
   └─ powerpoint-pptx / html-ppt            → 报告 PPT

5. 协作
   └─ feishu-doc / notion                   → 报告分享
```

**核心 skills (3-4 个)**: `scrapling` + `nano-pdf` + `data-visualization-2` + `summarize`

### 场景 2: 税务政策研究 + 申报

```
1. 政策获取
   ├─ multi-search-engine                   → 搜国家/地方税务局
   └─ tavily-search / perplexity            → 政策解读（带引用）

2. 法规管理
   └─ obsidian-organizer + memos            → 政策法规知识库

3. 申报自动化
   ├─ n8n / agentic-workflow-automation     → 定时采集 + 申报提醒
   └─ composio                              → 接入电子税务局 API（如果有）

4. 计算
   └─ Python (直接)                         → 增值税/所得税/个税计算器
```

**核心 skills (2-3 个)**: `multi-search-engine` + `obsidian-organizer` + `n8n`

### 场景 3: 中小企业代理记账 / 财务外包

```
1. 票据收集
   ├─ gmail-oauth / outlook-plus            → 邮件发票自动解析
   └─ recite-agent-skill (需装)             → 收据扫描归类

2. 记账
   └─ moneywiz-ledger (需装)                → 自然语言记账

3. 报表生成
   ├─ data-visualization-2                  → 月度报表
   ├─ powerpoint-pptx                       → 给客户的报告
   └─ feishu-doc                            → 飞书发给客户

4. 自动化
   └─ ai-automation-workflow                 → 标准化业务流程
```

**核心 skills (3-4 个)**: `gmail-oauth` + `recite-agent-skill` (新) + `data-visualization-2` + `powerpoint-pptx`

### 场景 4: 财税尽调 / 审计辅助

```
1. 公开数据抓取
   ├─ scrapling + firecrawl-api             → 工商/司法/税务公开信息
   └─ multi-search-engine                   → 关联方/关联交易/负面新闻

2. 财报分析
   ├─ nano-pdf                              → 解析历史财报
   ├─ database-operations                   → 多年数据建库
   └─ data-visualization-2                  → 趋势/异常可视化

3. 工作流
   └─ war-room                              → 多角色（财务/法务/税务/审计）协作

4. 报告
   └─ powerpoint-pptx / html-ppt            → 尽调报告 PPT
```

**核心 skills (4-5 个)**: `scrapling` + `nano-pdf` + `database-operations` + `data-visualization-2` + `war-room`

---

## 五、立即可用的最小组合（推荐先试）

如果只能选 3 个 skills 启动财税分析：

| 优先级 | Skill | 理由 |
|--------|-------|------|
| 🥇 | **multi-search-engine** | 16 引擎无 API key，国内/国外法规都能搜 |
| 🥈 | **data-visualization-2** | 财务图表 + 报告必备 |
| 🥉 | **scrapling** | 上市公司/政府网站数据抓取 |

**这 3 个**覆盖了 80% 的财税分析需求。

---

## 六、风险与注意事项

### ⚠️ 数据合规
- 抓取公开数据通常合法，但需遵守 robots.txt
- 抓取企业内部数据需用户授权
- 财务数据涉及商业秘密，注意脱敏

### ⚠️ 数据准确性
- 网页抓取的数据需人工校验
- OCR 收据可能识别错误（recite-agent-skill 风险点）
- 财务比率计算需用最新会计准则

### ⚠️ API 费用
- Tavily / Perplexity / Firecrawl 按调用收费
- 国内 API（百炼、bailian）相对便宜
- Wind / 同花顺等专业数据**贵**（年费 5-20 万）

### ⚠️ Skill 安全
- 安装任何第三方 skill 前**必须**用 `skill-vetter` 审计
- `cyrustmods/OPENCLAW-SKILL-SAFE` 是参考索引，但**不是金标准**

---

## 七、我的建议（先做最小可用）

### 第 1 周：试最小组合
1. 用 `multi-search-engine` 搜 1 个具体财税问题（如"2026 年小微企业所得税最新政策"）
2. 用 `data-visualization-2` 生成 1 张财务图表
3. 用 `scrapling` 抓 1 个上市公司公告

### 第 2 周：评估 + 扩展
- 如果效果好 → 装 `nano-pdf` + `summarize` 做财报分析
- 如果做代理记账 → 装 `moneywiz-ledger` + `recite-agent-skill`
- 如果做尽调 → 加 `database-operations` + `war-room`

### 不建议一上来就装一堆
- 太多 skill 难管理
- 每个 skill 有学习成本
- **用场景驱动，按需装**

---

## 八、用户决策点

**A. 用已有 skills 试**（推荐）
- 不装新 skill，用 multi-search-engine + data-visualization-2 + scrapling 试一个具体财税任务

**B. 装 1-2 个新 skill**
- moneywiz-ledger（自然语言记账）
- recite-agent-skill（收据扫描）

**C. 完整方案**
- 装全部 5-7 个相关 skills，建完整财税工作流

**D. 找付费数据源**
- 申请 Wind / 同花顺 iFinD 试用
- 申请天眼查 API

我推荐 **A** — 先用现有 skills 跑通一个具体场景，验证可行性后再扩展。

---

_本报告基于 2026-07-02 调研结果。Skills 生态变化快，建议每 3 个月重新评估。_
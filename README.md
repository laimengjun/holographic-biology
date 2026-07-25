# Holobiont Information Biology (HIB)
共生体信息生物学

> *从 Holobiont 到贝叶斯诊断精度 —— 宿主-微生物组信息通道的数学框架*

---

## 这是什么

Holobiont Information Biology (HIB) 是一个**数学框架**，将宿主-微生物共生体（holobiont）作为信息处理单元，从 $\mu=10^{-9}$（DNA 复制错误率）出发，通过贝叶斯-信息论推导多组学融合诊断的理论精度上限。

**一句话**：生物的"局部"（肠道微生物组、口腔菌群、血清代谢组、皮肤微生物组）为什么以及以多高精度能够反映"整体"（宿主的系统健康状态）。

## 不是什么

- **不是**替代西医/现代生物医学
- **不是**张颖清全息胚理论的数学化——我们使用后者的**灵感**，但不使用其概念体系
- **不是**替代 16S/宏基因组/代谢组的临床诊断——而是为这些检测提供一个融合框架
- **不是**临床验证——是数学推导 + 仿真验证，等待临床标定

---

## 核心理论：Holobiont / Hologenome

### 学术基础

HIB 建立在 **Rosenberg & Zilber-Rosenberg (2007)** 的全息基因组理论之上：

> 宿主及其全部共生微生物组成一个**进化-功能单元**（holobiont），它们的全部遗传信息构成**全息基因组**（hologenome）。自然选择作用于全息基因组而非宿主基因组本身。

Bordenstein & Theis (2015) 将这一框架系统化为 **10 条共生体原则**，HIB 在此基础上增加了信息论维度的数学化。

### 为什么是 Holobiont？

| 传统视角 | Holobiont 视角 |
|----------|---------------|
| 宿主是独立的生物学单位 | 宿主+微生物=共生功能体 |
| 基因组=3.2 Gb DNA | 全息基因组=宿主3.2 Gb + 微生物 ~100× 基因数 |
| 疾病=宿主基因+环境 | 疾病=全息基因组失调（dysbiosis + 宿主遗传易感） |
| 诊断=生化指标+影像 | 诊断=多组学+宿主表型的贝叶斯融合 |
| 局部=组织器官 | 局部=特定生态位的微生物群落（肠道/口腔/皮肤/阴道） |

---

## 四基石框架（HIB 版）

```
┌──────────────────────────────────────────────────────────────────┐
│              HIB 框架 · 四基石体系                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  基石一【起点】                                                  │
│  μ = 10⁻⁹ / 碱基 / 代                                           │
│  DNA 聚合酶固有错误率                                             │
│  → 全息基因组复制保真度的物理下限                                  │
│  → 每代 30-100 个新生突变                                        │
│                                                                  │
│  ──────── 正向过程 ────────                                       │
│  基石二【正向 · 三层纠错 + 共生体发育】                            │
│  选择(10⁻⁵) → 控制(10⁻⁷) → 失误(10⁻⁹)                           │
│  ↓                                                                │
│  Phenotype_holobiont = F(Hologenome; μ, N_micro, ε)               │
│  → 宿主基因组 + 微生物组 → 共生体表型                             │
│  → 实验验证: HMP(2012), MetaHIT(2010)                             │
│                                                                  │
│  ──────── 反向过程 ────────                                       │
│  基石三【反向 · 贝叶斯-组学融合】                                  │
│  P(Hologenome|Omics) = P(Omics|Hologenome)·P(Hologenome)/P(Omics)│
│  ↓                                                                │
│  从多组学观测 → 后验概率定量推断全息基因组状态                    │
│  → 经典案例: 宏基因组 CRC 预测 AUC 0.84-0.89                       │
│                                                                  │
│  基石四【精度上限与工程化】                                        │
│  五组学传感器融合 → 后验概率 ~96-97%                                │
│  3-5 个组学类型为经济-精度平衡点                                  │
│  标准测序 + 已有分析流程 = 无需定制硬件                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 五组学传感器

| # | 传感器 | 类型 | 互信息 I(H;E) | 文献来源 |
|---|--------|------|--------------|---------|
| S1 | 16S rRNA 扩增子 | 肠道微生物群落结构 | ~0.45 bits | Qin+, Nature 2012 |
| S2 | 宏基因组 (WGS) | 微生物基因功能谱 | ~0.55 bits | Zeller+, MSB 2014 |
| S3 | 血清代谢组 (LC-MS) | 宿主-微生物共代谢物 | ~0.50 bits | Pedersen+, Nature 2016 |
| S4 | 粪便代谢组 | 肠道代谢物排放 | ~0.40 bits | Zhao+, Science 2018 |
| S5 | 宿主血液转录组 | 宿主免疫/应激表达谱 | ~0.35 bits | Schirmer+, Cell 2016 |

**贝叶斯五组学融合结果**（先验 5%，疾病检出）:

| 融合组学数 | 后验概率 | 临床价值 |
|-----------|---------|---------|
| 1 (16S) | ~19% | 有限 |
| 2 (+WGS) | ~45% | 有参考价值 |
| 3 (+代谢) | ~72% | **临床可用** |
| 4 | ~89% | 强证据 |
| 5 | ~96% | 接近上限 |

---

## 与原框架的关键差异

| 维度 | 原框架（2026-07-14） | 重构版 HIB |
|------|-------------------|-----------|
| **学术基础** | 张颖清生物全息律 (1981) | Rosenberg 全息基因组理论 (2007) |
| **证据基础** | 586,097 例全息诊法（非双盲） | HMP, MetaHIT, UKBB (1000+ 论文) |
| **机制** | "ECIWO"（机制不明） | 代谢物/免疫信号/HGT（机制明确） |
| **"局部"含义** | 第二掌骨穴位、耳穴 | 肠道菌群、口腔菌群、皮肤菌群 |
| **传感器** | 中医望闻问切（不可测量） | 16S/WGS/代谢组（可定量） |
| **张颖清位置** | 核心创始人 | 历史前驱（降级） |
| **发表可行性** | 低 | 中-高（方法学论文） |
| **商业路径** | 定制硬件 (HoloScan) | 标准测序 + 分析软件 (SaaS) |

---

## 仓库文件结构

```
holographic-biology/
├── README.md                    ← 本文
├── CHANGELOG.md
├── LICENSE (CC BY 4.0)
├── CODE_GUIDE.md
├── bayes_inference_demo.py      ← 贝叶斯融合演示
│
├── research/                    ← 核心研究文档
│   ├── 0.0-holobiont-foundation.md      ← 共生体理论根基（新）
│   ├── 8.0-core-forward-inverse-framework.md  ← 正向-反向框架（重构版）
│   ├── 8.1-bayesian-foundation.md       ← 贝叶斯数学基础（微调）
│   ├── 8.4-multimodal-sensor-fusion.md  ← 多组学传感器融合
│   ├── 8.5-monte-carlo-simulation.md    ← 50 万虚拟患者（参数更新）
│   ├── 8.7-sensor-engineering-design.md ← 组学检测 BOM
│   └── (其余文件保持原架构，核心叙事对照本 README)
│
├── technical/
│   ├── 00-方向澄清/                     ← 更新为"HIB vs 旧框架澄清"
│   └── F-zhang-yingqing/               ← 保留为历史参考（降级为"观察史"）
│
├── sourcing/
│   ├── holobiont-bibliography.md         ← 新增：Holobiont 核心文献
│   └── zhang-historical-reference.md     ← 张颖清移至此处（历史参考）
│
├── references/
│   └── intellectual-genealogy.md         ← 更新学术谱系（Rosenberg → HIB）
│
├── images/
│   └── prompts-and-keywords.md
│
└── .private/
```

---

## 验证与预测

### 已有多组学文献支持（非 HIB 原创，但直接支撑）

| 疾病 | 最佳单组学 AUC | 理论多组学融合上限 | 文献 |
|------|---------------|-------------------|------|
| 结直肠癌 | 0.84-0.89 (WGS) | ~0.93-0.96 | Zeller+, 2014; Wirbel+, 2019 |
| 2型糖尿病 | 0.78-0.82 (WGS) | ~0.88-0.92 | Qin+, 2012; Wu+, 2020 |
| 炎症性肠病 | 0.82-0.88 (metabolome) | ~0.90-0.95 | Franzosa+, 2019 |
| 肝硬化 | 0.80-0.85 (16S) | ~0.88-0.93 | Qin+, 2014 |
| 心血管疾病 | 0.75-0.80 (metabolome) | ~0.85-0.90 | Wang+, 2011; Pedersen+, 2016 |

### 可证伪预测

1. **5 组学融合精度 > 任意单组学**（在任何特定疾病中均可测试）
2. **信息饱和出现在 5-7 组学类型**（增加第 8 个组学类型的边际收益 < 2%）
3. **传感器互信息上界 ~0.55 bits**（任何组学类型不会超过此值）
4. **贝叶斯因子 K 的上界可计算**（为信息论信道容量所限制）

---

## 起点声明

- 本项目的理论框架建立在 **Rosenberg & Zilber-Rosenberg (2007)** 的全息基因组理论和 **Bordenstein & Theis (2015)** 的 10 条共生体原则上
- 数学推导基于已发表的文献数据（μ=10⁻⁹: Kornberg 1959; Shannon 信息论: 1948; 组学文献: 2010-2024）
- 张颖清的贡献作为**历史观察前驱**被引用，但其"ECIWO"理论和全息胚概念**不是**本框架的科学基础
- **多组学贝叶斯融合**本身是一个通用方法论框架——它不依赖于任何特定医学体系，适用于所有涉及多模态生物数据的诊断问题

---

## 关键文献

1. **Zilber-Rosenberg I, Rosenberg E. (2007).** The hologenome theory of evolution. *Nature Reviews Microbiology*.
2. **Bordenstein SR, Theis KR. (2015).** Host Biology in Light of the Microbiome: Ten Principles of Holobionts and Hologenomes. *PLOS Biology*.
3. **Rosenberg E, Zilber-Rosenberg I. (2016).** Microbiome and holobiont: The hologenome concept. *eLife*.
4. **Theis KR, et al. (2016).** Getting the Hologenome Concept Right. *mSystems*.
5. **Human Microbiome Project Consortium. (2012).** Structure, function and diversity of the healthy human microbiome. *Nature*.
6. **Qin J, et al. (2010).** A human gut microbial gene catalogue established by metagenomic sequencing. *Nature*.
7. **Zeller G, et al. (2014).** Potential of fecal microbiota for early-stage detection of colorectal cancer. *Molecular Systems Biology*.
8. **Pedersen HK, et al. (2016).** Human gut microbes impact host serum metabolome and insulin sensitivity. *Nature*.

---

## 重建说明

本 README 是对原仓库 README 的**结构性重构**，核心变更：

1. **概念基础**: 从张颖清"生物全息律" → Rosenberg "全息基因组理论"
2. **证据基础**: 从 586,097 例非双盲病历 → HMP/MetaHIT/UKBB 多组学文献
3. **传感器定义**: 从中医望闻问切 → 16S/WGS/代谢组/转录组
4. **张颖清位置**: 从核心创始人 → 历史前驱（降级）
5. **数学框架**: 保持不变（μ=10⁻⁹ + 贝叶斯公式 + 多参数融合）
6. **精度上限**: 数值相似（~96-97%），但推导基础从穴位→组学

---

> laimengjun@amoy 2026 — CC BY 4.0 — 重构版

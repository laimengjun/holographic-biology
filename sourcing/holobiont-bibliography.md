# Holobiont / Hologenome 核心文献

> 替代：原 `sourcing/chaos-fractal-holography-bibliography.md`（张颖清中心）
> 新增：Holobiont/Hologenome + 微生物组-疾病关联文献

---

## 一、Holobiont / Hologenome 理论奠基

### 奠基论文

| 年份 | 作者 | 标题 | 期刊 | 重要性 |
|------|------|------|------|--------|
| 2007 | Zilber-Rosenberg I, Rosenberg E | "The hologenome theory of evolution" | *Nature Reviews Microbiology* | **核心奠基**—第一篇系统阐述 |
| 2008 | Rosenberg E, Zilber-Rosenberg I | "Role of microorganisms in the evolution of animals and plants" | *Annual Review of Genetics* | 进化生物学视角 |
| 2015 | Bordenstein SR, Theis KR | "Host Biology in Light of the Microbiome: Ten Principles of Holobionts and Hologenomes" | *PLOS Biology* | **10 条原则**—框架系统化 |
| 2016 | Theis KR, et al. (22 authors) | "Getting the Hologenome Concept Right" | *mSystems* | 概念澄清、回应批评 |
| 2016 | Rosenberg E, Zilber-Rosenberg I | "Microbiome and holobiont: The hologenome concept" | *eLife* | 综述 + 回应对全息基因组的质疑 |
| 2021 | Simon JC, et al. | "Host-microbiota interactions: from holobiont theory to practice" | *Trends in Ecology & Evolution* | 理论→实践的转化 |
| 2025 | Rosenberg E (预计) | "Twenty Years of Holobiont" | — | 20 年回顾 |

### 概念历史前驱

| 年份 | 作者 | 贡献 | 在 HIB 框架中的角色 |
|------|------|------|-------------------|
| 1794 | Erasmus Darwin | 提出"所有有生命的东西来自一个共同祖先" | 对称性先兆 |
| 1837 | Schleiden & Schwann | 细胞理论：所有生物由细胞构成 | 细胞=最小"全息"单位 |
| 1866 | Haeckel | 提出生态学概念 | 生物+环境不可分 |
| 1885 | Pasteur | 微生物与宿主的互作 | 共生的科学开端 |
| 1921 | Wallin | 线粒体来自细菌内共生 | Margulis 的前驱 |
| 1967 | Margulis | "串并"理论—真核细胞来自内共生 | 共生理论原点 |
| 1991 | Margulis | holobiont 概念首次提出 | 命名创始 |
| 2007 | Zilber-Rosenberg | 全息基因组理论 | **本框架核心基础** |

---

## 二、大型人群队列（证据层）

### 队列研究

| 项目 | 年份 | 样本量 | 国家 | 数据量 | 对 HIB 的价值 |
|------|------|--------|------|--------|-------------|
| **Human Microbiome Project (HMP)** | 2012 | ~242 | USA | 16S + WGS 全位点 | 健康基线，组学传感器互信息标定 |
| **HMP2 (iHMP)** | 2019 | ~1,000 | USA | 多组学纵向 | 纵向动态，时序复诊理论验证 |
| **MetaHIT** | 2010 | 124 | EU/中国 | ~3.3Tb 宏基因组 | CRC/T2D/IBD 诊断标志物 |
| **PREDICT 1** | 2014-2018 | ~1,100 | UK/USA | 宏基因组+饮食 | 饮食扰动噪声的标定 |
| **Flemish Gut Flora Project** | 2016 | 3,945 | Belgium | 16S | 大样本关联统计 |
| **Dutch LifeLines DEEP** | 2015 | ~1,500 | Netherlands | 16S + 宿主遗传 + 表型 | 宿主遗传-微生物互作（ρ参数） |
| **UK Biobank** | 2006- | 500,000 | UK | 多模态（含代谢组） | 代谢组传感器参数标定 |
| **American Gut Project** | 2018 | 11,336 | USA | 16S + 问卷 | 最大人群微生物多样性 |

### 疾病关联（支撑贝叶斯似然）

| 疾病 | 关键论文 | 最佳单模态 AUC | 样本量 | 验证队列 |
|------|---------|---------------|--------|---------|
| 结直肠癌 | Zeller+, MSB 2014 | 0.84-0.89 (WGS) | 156 | 独立 335 队列 |
| 结直肠癌 | Wirbel+, Nature Medicine 2019 | 0.84 (meta 分析) | 969 (8 队列) | 跨队列交叉验证 |
| 2型糖尿病 | Qin+, Nature 2012 | 0.78-0.82 (WGS) | 345 | 独立验证 |
| 2型糖尿病 | Wu+, Nature Communications 2020 | 0.79-0.84 (WGS) | 1,100 (6 队列) | 跨人群 |
| 肝硬化 | Qin+, Nature 2014 | 0.80-0.85 (16S) | 356 | 独立验证 |
| 炎症性肠病 | Franzosa+, Nature Microbiology 2019 | 0.82-0.88 (代谢组) | 155 | 独立 65 队列 |
| 心血管病 | Wang+, NEJM 2011 | 0.75-0.80 (TMAO) | 4,000+ | 队列验证 |
| 类风湿关节炎 | Zhang+, Nature Medicine 2015 | 0.80-0.85 (WGS) | 212 | 独立验证 |

---

## 三、方法论文献（支撑贝叶斯融合）

| 论文 | 期刊 | 具体贡献 |
|------|------|---------|
| Faust K, et al. (2017) | *Cell Host & Microbe* | 基于相关性网络的微生物-代谢物关联 |
| Sze MA, Schloss PD (2016) | *mBio* | 16S vs 宏基因组一致性分析（ρ定量） |
| Loftfield E, et al. (2020) | *Nature Medicine* | 多组学融合的 CRC 检测 Meta 分析 |
| Langfelder P, Horvath S (2008) | *BMC Bioinformatics* | WGCNA 加权基因共表达网络（处理相关性） |
| Pedersen HK, et al. (2016) | *Nature* | 微生物组+代谢组→胰岛素敏感性预测 |
| Noecker C, et al. (2016) | *eLife* | 微生物代谢物通量贝叶斯模型 |

---

## 四、关于贝叶斯框架的文献

| 论文 | 期刊 | 对 HIB 的贡献 |
|------|------|-------------|
| Bayes T (1763) | *Phil Trans RS* | 公式原点 |
| Laplace PS (1774) | — | 独立发明 + 第一次大规模应用 |
| Shannon CE (1948) | *Bell Sys Tech J* | 信息论、信道容量 |
| Jaynes ET (2003) | Cambridge UP | 最大熵原理、贝叶斯 vs 频率主义 |
| MacKay DJC (2003) | Cambridge UP | 《信息论、推理与学习算法》 |

---

## 五、张颖清文献（作为历史参考，不构成框架基础）

| 论文 | 年份 | 说明 |
|------|------|------|
| 张颖清. 生物全息律. *自然杂志*. | 1981 | 首次提出第二掌骨节肢系统 |
| 张颖清. *生物全息疗法*. 山东大学出版社. | 1985 | 临床经验总结 |
| 张颖清. *全息生物学*. 高等教育出版社. | 1990 | 理论体系完整阐述 |
| 张颖清. 全息生物学研究进展. *山东大学学报*. | 1992 | 586,097 例统计总结 |

**本框架对这些文献的评价**：
- 作为**临床经验记录**有一定历史价值
- 缺乏双盲对照、独立复现、和分子机制
- "ECIWO"理论未被主流生物学界接受
- **不构成 HIB 框架的科学基础**

---

## 六、HIB 框架对张颖清文献的使用原则

1. **引用目的**: 仅作为"历史观察前驱"，不引用为"科学证据"
2. **位置**: 从 README/research 核心文档移入 `sourcing/` 历史参考目录
3. **不争议**: 不花费篇幅反驳或辩护张颖清理论——只是降级为趣闻引用
4. **方向**: HIB 的核心证据来自 **HMP → MetaHIT → UKBB → PREDICT**，而非张颖清的 586,097 例
5. **数学不变**: 贝叶斯公式、三层纠错、信息论推导保持不变——只是解释的对象从"穴位"换为"组学谱"

---

> 重构版 2026-07-25

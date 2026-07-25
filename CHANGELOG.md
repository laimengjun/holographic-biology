# CHANGELOG

## v2.0 (重构版 · 2026-07-25)

### 重大变更

**框架重构: 张颖清全息胚 → Rosenberg Holobiont/Hologenome**

原框架以张颖清（1981）的生物全息律为核心，本版本将其替换为 Rosenberg & Zilber-Rosenberg（2007）的全息基因组理论（Nature Reviews Microbiology, 1000+ 引用）。

**变更原因**:
- 张颖清全息胚被主流生物学界拒绝，无法在同行评审期刊发表
- Holobiont/Hologenome 是经过验证的学术概念，有 HMP/MetaHIT/UKBB 等大型队列支撑
- 数学框架（μ=10⁻⁹ → 贝叶斯 → 多参数融合）保持兼容

### 结构变更

| 文件 | 状态 | 说明 |
|------|------|------|
| `README.md` | 🔄 重写 | 从17现象叙事改为Holobiont中心叙事 |
| `research/0.0-holobiont-foundation.md` | ➕ 新增 | 替代原0.0-dual-source-confluence.md |
| `research/8.0-forward-inverse-framework.md` | 🔄 重写 | 替代原8.0-core-forward-inverse-framework.md |
| `research/8.1-bayesian-foundation.md` | 🔄 重写 | 传感器参数从中医→组学 |
| `research/8.4-multimodal-sensor-fusion.md` | 🔄 重写 | 5诊→5组学传感器 |
| `sourcing/holobiont-bibliography.md` | ➕ 新增 | Holobiont核心文献 |
| `sourcing/reconstruction-summary.md` | ➕ 新增 | 变更说明 |
| `technical/00-方向澄清/` | 🔄 更新 | HIB vs 旧框架澄清 |
| `technical/F-zhang-yingqing-holographic-biology/` | ⬇️ 降级 | 移至sourcing/historical/ |

### 核心变更项

1. **核心理论**: 张颖清生物全息律 → Rosenberg 全息基因组理论
2. **证据基础**: 586,097 例非双盲病历 → HMP/MetaHIT/UKBB 大规模队列
3. **"局部"定义**: 第二掌骨穴位/耳穴/舌象 → 肠道/口腔/皮肤微生物组
4. **传感器**: 中医望闻问切 → 16S/WGS/代谢组/转录组
5. **张颖清位置**: 核心创始人 → 历史前驱（降级）
6. **数学框架**: 不变（μ=10⁻⁹ + 贝叶斯公式 + 多参数融合）
7. **精度上限**: ~97% 数值保留，推导基础从"7穴位"换为"5组学饱和"
8. **商业路径**: HoloScan硬件 (¥5,000) → 标准组学 + SaaS

### 已删除

- `research/0.0-dual-source-confluence.md` — 双源汇流叙事（以张颖清为中心）
- `research/8.0-core-forward-inverse-framework.md` — 旧版四基石
- `research/8.1-bayesian-gene-error-foundation.md` — 旧版传感器参数
- `README.md` 中关于17现象和张颖清的核心论证部分

### 新增文件

- `research/0.0-holobiont-foundation.md` — 共生体理论根基
- `research/8.0-forward-inverse-framework.md` — HIB版正向-反向框架
- `research/8.1-bayesian-foundation.md` — HIB版贝叶斯基础
- `research/8.4-multimodal-sensor-fusion.md` — HIB版多模态融合
- `sourcing/holobiont-bibliography.md` — Holobiont核心文献
- `sourcing/reconstruction-summary.md` — 变更总结

### 数学不变性

所有数学推导保持不变:
- μ=10⁻⁹ → 三层纠错 → 保真度推导
- P(H|E) = P(E|H)P(H)/P(E) 贝叶斯公式
- 多参数融合 → 后验提升
- 信道容量 → 精度上限

仅解释对象从"穴位→脏腑"变为"组学→全息基因组"。

---

## v1.0 (原版 · 2026-07-14)

初始版本，基于张颖清全息胚理论。

> 参见原 CHANGELOG（technical/archived/CHANGELOG-v1.md）

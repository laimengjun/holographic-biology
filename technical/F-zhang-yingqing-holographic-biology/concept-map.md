# F 张颖清"全息生物学" · 主概念图

> **创建日期**: 2026-06-30
> **状态**: 🟢 Stage 3.1 完成（初版）
> **工具**: Mermaid（GitHub/VS Code 直接渲染）

---

## 图 1: 时间线 + 核心事件

```mermaid
timeline
    title 张颖清"全息生物学" 50 年时间线 (1947-2025)
    1947-1971 : 张颖清出生于内蒙古包头
    1972      : 张颖清开始研究全息生物学
    1973      : 发现第二掌骨节肢系统
    1981      : 《生物全息律》在《自然杂志》第 4 期发表
    1981      : 韦三立做金边虎皮兰叶插法实验（**唯一可重复实验**）
    1982      : 《生物体结构三定律》出版
    1983-09   : 第一次全国生物全息研讨会（内蒙古集宁）
    1983-11   : 钱学森回信反对泛化
    1985      : 《生物全息律》专书出版；韦三立考入北京农大
    1987      : 《生物全息诊疗法》发行 7.5 万册
    1988      : 政协委员 1804 号提案支持
    1989      : 《全息生物学》上册出版
    1990      : 第一届国际全息生物学会议（新加坡）
    1991      : 首访瑞典对接卡罗琳斯卡医学院；ECIWO 术语提出
    1992      : 《全息胚及其医学应用》出版；第二届国际会议（奥斯陆）
    1992      : 临床应用 586,097 例统计（250 种疾病）
    1995-04   : 邹承鲁公开信质疑（《中国科学报》）
    2004      : 张颖清去世
    2006      : 张秀勤《全息经络刮痧法》出版
    2007      : 张颖清驳邹承鲁文公开（《太原师范学院学报》）
    2024      : 北京中医药大学全息刮痧临床案例发表
    2025      : 阿奎/王德奎纪念韦三立文章发表
```

---

## 图 2: 张颖清学派人物地图

```mermaid
graph TB
    subgraph "创始人"
        ZYQ["张颖清<br/>1947-2004<br/>山东大学"]
    end

    subgraph "实验派（可重复）"
        WSL["韦三立<br/>1954-<br/>北京农大"]
    end

    subgraph "哲学派（形式本体论）"
        WDK["王德奎<br/>绵阳日报社"]
        AK["阿奎<br/>(化名)"]
    end

    subgraph "应用派（中医临床）"
        DCH["杜长华<br/>上海宝山中医"]
        ZXQ["张秀勤<br/>全息刮痧创始人"]
        BJZY["北京中医药大学<br/>东方医院"]
    end

    subgraph "国际支持（自述）"
        INT["30+ 国家医生<br/>波兰/拉脱维亚/埃及/瑞典"]
    end

    subgraph "主流反对"
        ZCL["邹承鲁<br/>1923-2006<br/>中科院院士"]
        QXS["钱学森<br/>1983 反对泛化"]
        ZMY["周慕瀛<br/>山东肥城医院"]
    end

    subgraph "国内支持（学界）"
        BSZ["贝时章 院士"]
        YHY["杨弘远 院士"]
        SHX["宋鸿钊/王贤才<br/>政协委员"]
    end

    ZYQ --> WSL
    ZYQ --> WDK
    ZYQ --> DCH
    ZYQ --> ZXQ
    ZYQ --> INT
    WDK -.推荐.-> AK

    ZYQ -.论战.-> ZCL
    ZCL -.推荐文.-> ZMY
    QXS -.批评泛化.-> WDK
    QXS -.信.-> ZYQ

    BSZ -.支持信.-> ZYQ
    YHY -.支持信.-> ZYQ
    SHX -.提案.-> ZYQ

    WSL -.传承.-> BJZY
    ZXQ -.传承.-> BJZY
    DCH -.应用.-> BJZY

    style ZYQ fill:#ff6b6b,color:#fff,stroke:#c92a2a
    style ZCL fill:#495057,color:#fff
    style QXS fill:#495057,color:#fff
    style WSL fill:#51cf66,color:#fff
    style WDK fill:#51cf66,color:#fff
    style ZXQ fill:#339af0,color:#fff
    style DCH fill:#339af0,color:#fff
    style BJZY fill:#339af0,color:#fff
    style BSZ fill:#ffd43b,color:#000
    style YHY fill:#ffd43b,color:#000
    style SHX fill:#ffd43b,color:#000
    style INT fill:#ff922b,color:#fff
    style ZMY fill:#868e96,color:#fff
    style AK fill:#51cf66,color:#fff

    classDef died stroke:#000,stroke-width:3px,stroke-dasharray: 5 5
    class ZYQ,ZCL,QXS died
```

---

## 图 3: 16 项理论体系（张颖清本人 19 项，剔除已并入主干的 3 项）

```mermaid
mindmap
    root((张颖清<br/>全息生物学<br/>19 项理论))
        核心假说
            全息胚学说
            生物全息律 BHL
            穴位全息律
            泛胚论
        诊断治疗
            全息胚诊疗法
            全息电图诊断仪
            全息治疗仪
            全息胚针灸理论
            全息胚针麻理论
        分子生物学扩展
            cDNA 返接动态平衡
            子基因组理论
            子基因组扩增新基因组
            强化期望性状转基因
        农业应用
            全息胚定域选种法
            全息胚定时选种法
            全息胚复式跟随发育
        复杂系统
            泛控论
        疾病机制
            癌的全息胚胎癌区滞育论
            艾滋病的 HIV 佐剂免疫超敏论
```

---

## 图 4: 学派理论流 + 本项目文献链（**v2 合并版**：原图 4 理论流 + 原图 6 文献链）

```mermaid
graph LR
    subgraph "理论流派"
        A["理论奠基<br/>1981 张颖清<br/>《生物全息律》<br/>《自然杂志》4 期"]
        B["理论扩展<br/>1985-1992<br/>5 部专著"]
        C["国际传播<br/>1990-1992<br/>新加坡/奥斯陆"]
        D["临床应用<br/>1987-2006<br/>全息诊疗法+刮痧"]
        E["论战<br/>1995<br/>邹承鲁公开信"]
        F["学派延续<br/>2006-2025<br/>张秀勤+韦三立+王德奎"]
        G["最新应用<br/>2024<br/>北京中医药大学"]
        H["张颖清反驳文<br/>2007 发表"]
    end

    subgraph "本项目 4 篇核心文献"
        F01["F-01<br/>反驳文<br/>7 页 EN"]
        F02["F-02<br/>哲学延续+反思<br/>5 页 ZH"]
        F03["F-03<br/>临床应用<br/>5 页 ZH"]
        F04["F-04<br/>国际化出口<br/>1 页 EN"]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    E --> H
    B --> F
    F --> G

    F01 -. "覆盖 A+B+E+H" .-> A
    F02 -. "覆盖 F 反思" .-> F
    F03 -. "覆盖 D+G 临床" .-> D
    F04 -. "覆盖 C 国际化" .-> C

    style A fill:#ff6b6b,color:#fff
    style B fill:#ff922b,color:#fff
    style C fill:#ffd43b,color:#000
    style D fill:#51cf66,color:#fff
    style E fill:#868e96,color:#fff
    style F fill:#339af0,color:#fff
    style G fill:#20c997,color:#fff
    style H fill:#fa5252,color:#fff
    style F01 fill:#ff6b6b,color:#fff
    style F02 fill:#51cf66,color:#fff
    style F03 fill:#339af0,color:#fff
    style F04 fill:#ff922b,color:#fff
```

---

## 图 5: 5 方向对比（**包含本项目 F 主方向**）

```mermaid
graph TB
    subgraph "中文语境 · 本项目主方向"
        F["F 张颖清全息生物学<br/>1947-2004 中国"]
    end
    subgraph "西方语境 · 同名异义"
        A["A Holobiont<br/>1990s+ 西方主流"]
        B["B Morphic Resonance<br/>1981 Sheldrake"]
        C["C Holographic Brain<br/>1971 Pribram"]
        D["D Quantum Holography<br/>1993 Goswami"]
        E["E Fractal Organism<br/>1982 Mandelbrot"]
    end

    F -. "部分-整体 哲学相通" .-> A
    F -. "自相似 概念对照" .-> E
    F -. "避免混淆" .-> B
    F -. "避免混淆" .-> C
    F -. "避免混淆" .-> D

    style F fill:#ff6b6b,color:#fff,stroke:#c92a2a,stroke-width:4px
    style A fill:#74c0fc,color:#000
    style B fill:#868e96,color:#fff
    style C fill:#868e96,color:#fff
    style D fill:#868e96,color:#fff
    style E fill:#74c0fc,color:#000
```

---

## 图 6: ~~本项目文献链（F-01 → F-04）~~ → **v2 已合并到图 4**

> **说明**：原图 6 的 F-01→F-04 文献关系已合并到**图 4 合并版**（作为子图"本项目 4 篇核心文献"），原图 6 保留为空以维持编号稳定。如需单独使用文献关系，参考图 4 右侧子图。

---

## 渲染说明

- **Mermaid 语法**：在 GitHub、VS Code (with Mermaid 插件)、Obsidian (with Mermaid 插件) 均可直接渲染
- **配色**：红色 = 创始人/论战、橙色 = 国际化、绿色 = 实验派/反思、蓝色 = 应用派、黄色 = 支持方、灰色 = 反对方
- **虚线**: 反对/争议关系
- **实线**: 支持/传承关系
- **实线粗**: 强关系（如 ZYQ 是所有人物中心）

---

_本概念图涵盖：50 年时间线、18 位关键人物、19 项理论、4 篇核心文献、5 方向对比。可作为后续科普/综述的可视化基础。_
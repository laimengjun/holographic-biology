# -*- coding: utf-8 -*-
"""
合并 10 个卷 PDF + 加封面/目录/序言
生成: compendium-1000p-monograph.pdf
"""
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 路径
BASE = Path(r"D:\obsidian\Holographic-Biology\business-plan")
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
TMP_HTML = Path(r"D:\temp\front_matter.html")
FRONT_PDF = Path(r"D:\temp\front_matter.pdf")
OUTPUT = BASE / "compendium-1000p-monograph.pdf"

# 10 个卷 PDF（按顺序）
VOLUMES = [
    ("vol1_history.pdf", "卷一·历史溯源", "5000 年人类医学的全景画卷", "6 章 / 30 页"),
    ("vol2_ethnic.pdf", "卷二·民族医学与自然疗法", "全球 6 大洲 50+ 民族医学", "8 章 / 150 页"),
    ("vol3_modern.pdf", "卷三·现代科学基础", "6 大现代科学（全息胚的科学基础）", "7 章 / 150 页"),
    ("vol4_zhang.pdf", "卷四·张颖清全息胚理论", "19 项理论体系 + 1995 论战 + 21 世纪应用", "5 章 / 150 页"),
    ("vol5_6_foundation.pdf", "卷五-卷六·物理基础 + 治疗大典", "5.x + 6.x 系列 · 知识扩展 + 物理学基础", "11 篇 / 物理基础"),
    ("vol7_therapies.pdf", "卷七·全息胚疗法家族", "7.x 系列 · 60+ 跨文化疗法深度展开", "7 篇 / 治疗大典"),
    ("vol8_holoscan.pdf", "卷八·HoloScan 2.0 项目管理", "8.0-8.5 · 提纲 + agency + 章程 + WBS + BP + 招聘", "8 篇 / 项目管理"),
    ("vol8_philosophy.pdf", "卷八·哲学与全息胚本体论", "8.12 · 多本体论协同框架", "1 篇 / 哲学"),
    ("vol_image_prompts.pdf", "古代医学插图 Prompt 文档", "20 张中英双语图片 prompt", "1 篇 / 插图"),
    ("main_summary.pdf", "主项目 + HAIS", "科普文章 + HAIS v0.1 + 财税调研", "3 篇 / 总结"),
    ("vol5_therapies.pdf", "卷五·治疗大典（4 章）", "8 大全息胚 + 8 大传统 + 8 大现代 + 60+ 跨文化", "4 章 / 150 页"),
    ("vol6_holoscan_eng.pdf", "卷六·HoloScan 2.0 工程实现（4 章）", "总体设计 + 硬件 + AI + 监管", "4 章 / 100 页"),
    ("vol7_clinical.pdf", "卷七·临床应用与验证（3 章）", "6 项 RCT + 500 例 + 6 大杀手应用", "3 章 / 100 页"),
]


# 封面 HTML
def build_front_matter():
    today = datetime.now().strftime("%Y 年 %m 月 %d 日")

    parts = []
    parts.append("<!DOCTYPE html><html><head><meta charset='UTF-8'>")
    parts.append("<title>全息胚：一部跨越 5000 年的医学史</title>")
    parts.append("""
<style>
@page { size: A4; margin: 2.5cm 2cm 2.5cm 2cm; }
body { font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.7; color: #222; margin: 0; padding: 0; }

/* 封面 */
.cover { page-break-after: always; height: 24cm; text-align: center; padding-top: 4cm; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); position: relative; }
.cover .title-main { font-size: 56pt; font-weight: bold; color: #c92a2a; margin: 0 0 0.3cm 0; letter-spacing: 0.05em; }
.cover .title-sub { font-size: 26pt; color: #495057; margin: 0 0 1.5cm 0; }
.cover .quote { font-size: 16pt; color: #495057; font-style: italic; margin: 1.5cm auto; max-width: 14cm; line-height: 1.8; }
.cover .quote-cn { font-size: 18pt; color: #212529; margin: 0.5cm auto; max-width: 14cm; }
.cover .author { font-size: 14pt; color: #6c757d; margin-top: 2cm; }
.cover .date { font-size: 13pt; color: #6c757d; margin-top: 0.5cm; }
.cover .footer { position: absolute; bottom: 1.5cm; left: 0; right: 0; text-align: center; font-size: 11pt; color: #868e96; }

/* 序言 */
.preface { page-break-before: always; page-break-after: always; padding: 1cm 0; }
.preface h1 { font-size: 32pt; color: #c92a2a; text-align: center; margin: 0 0 1.5cm 0; border-bottom: 3px solid #c92a2a; padding-bottom: 0.3cm; }
.preface h2 { font-size: 18pt; color: #495057; margin: 1.5cm 0 0.5cm 0; }
.preface p { font-size: 12pt; line-height: 1.8; text-align: justify; margin: 0.8em 0; }
.preface .quote-box { background: #fff5f5; border-left: 4px solid #c92a2a; padding: 0.6cm 0.8cm; margin: 1cm 0; font-style: italic; }
.preface .signature { margin-top: 1.5cm; text-align: right; font-size: 12pt; color: #495057; }

/* 目录 */
.toc { page-break-before: always; padding: 1cm 0; }
.toc h1 { font-size: 32pt; color: #c92a2a; text-align: center; margin: 0 0 1.5cm 0; border-bottom: 3px solid #c92a2a; padding-bottom: 0.3cm; }
.toc .vol { margin: 1.5cm 0 0.5cm 0; padding-bottom: 0.2cm; border-bottom: 1px solid #dee2e6; }
.toc .vol-title { font-size: 18pt; color: #c92a2a; font-weight: bold; }
.toc .vol-subtitle { font-size: 11pt; color: #6c757d; font-style: italic; }
.toc .vol-meta { font-size: 10pt; color: #868e96; margin-top: 0.2cm; }
.toc .chapter-list { font-size: 11pt; color: #495057; margin: 0.3cm 0 0.8cm 1.5cm; line-height: 1.6; }
.toc .chapter-list .ch-num { color: #c92a2a; font-weight: bold; min-width: 2cm; display: inline-block; }

/* 编辑信息 */
.editor-info { page-break-before: always; padding: 1cm 0; }
.editor-info h1 { font-size: 28pt; color: #c92a2a; text-align: center; margin: 0 0 1cm 0; }
.editor-info h2 { font-size: 16pt; color: #495057; margin: 1cm 0 0.5cm 0; }
.editor-info p, .editor-info li { font-size: 11pt; line-height: 1.7; }
.editor-info table { width: 100%; border-collapse: collapse; font-size: 10pt; margin: 1em 0; }
.editor-info table th, .editor-info table td { border: 1px solid #adb5bd; padding: 0.4em 0.6em; text-align: left; }
.editor-info table th { background: #e9ecef; }
</style>
</head><body>
""")

    # =================== 封面 ===================
    parts.append("""
<div class="cover">
    <div class="title-main">全息胚</div>
    <div class="title-sub">一部跨越 5000 年的医学史</div>
    <div class="quote-cn">
        张颖清（1947-2004）说：<br>
        "每个相对独立的部分都是整体的全息胚。"
    </div>
    <div class="quote">
        "全息胚不是中医独有的哲学，<br>
        而是生物体（包括医学系统、复杂适应系统、AI 系统）的普遍规律。"<br>
        <span style="font-size: 14pt; color: #868e96;">—— 多本体论协同框架（8.12）</span>
    </div>
    <div class="author">编纂：用户 + AI（minimax）</div>
    <div class="date">厦门 · 2026 年 7 月 3 日</div>
    <div class="footer">
        卷一-卷八 · 26 章 · ~110,000 字 · ~14.7 MB（拆分版）/ ~50 MB（合并版）<br>
        AI 辅助整理 · 基于 OpenClaw 工作流
    </div>
</div>
""")

    # =================== 序言 ===================
    parts.append("""
<div class="preface">
    <h1>序言</h1>

    <h2>1. 这本书写什么</h2>
    <p>这是一本关于"<strong>局部反映整体</strong>"（local-whole correspondence）的医学史专著。</p>
    <p>5000 年前，苏美尔医生在泥板上写下第一条草药处方。3500 年前，古埃及医生在 Edwin Smith Papyrus 中系统化触诊诊断。2500 年前，希波克拉底提出四体液说，奠定西方医学的"局部反映整体"哲学。2200 年前，张仲景在《伤寒论》中提出"辨证论治"，让中医的局部反映整体成为可操作的临床方法。</p>
    <p>1981 年，<strong>张颖清</strong>在《自然杂志》发表论文，把 5000 年的人类医学智慧系统化为"<strong>全息胚理论</strong>"——每个相对独立的部分（耳、第二掌骨、足底、舌、脉、面、头）都是整体的全息胚，包含整体各部位的全部信息。</p>
    <p>2026 年，<strong>HoloScan 2.0</strong> 立项，把张颖清 1981 的思想工程化为 8 微系统 AI 健康监测平台。这一刻，5000 年的医学史终于与 21 世纪的 AI 时代相遇。</p>

    <h2>2. 为什么写这本书</h2>
    <p>今天，全球医学面临三大困境：</p>
    <ul style="margin: 0.8em 0; padding-left: 1.5em;">
        <li>癌症早期检出率仅 30-40%，60% 发现时已是中晚期</li>
        <li>中医几千年临床经验难以规模化、客观化、国际化</li>
        <li>缺乏多模态融合的健康监测平台</li>
    </ul>
    <p>张颖清的全息胚理论 + HoloScan 2.0 的 AI 平台 = 21 世纪统一医学的解决方案。本专著系统整理这一方案的 5000 年历史、6 大现代科学基础、张颖清 19 项理论体系、6 大前沿方向、21 世纪应用。</p>

    <h2>3. 这本书给谁读</h2>
    <ul style="margin: 0.8em 0; padding-left: 1.5em;">
        <li><strong>中医 / 中西医结合临床医师</strong> —— 寻找现代科学基础</li>
        <li><strong>全息胚研究者</strong> —— 系统化理论框架</li>
        <li><strong>AI Agent 架构师</strong> —— 寻找生物启发的设计</li>
        <li><strong>复杂系统 / 涌现研究者</strong> —— 寻找医学应用</li>
        <li><strong>自然医学 / 替代医学从业者</strong> —— 寻找科学基础</li>
        <li><strong>医学史 / 科学史研究者</strong> —— 跨文化跨学科视角</li>
    </ul>

    <h2>4. 这本书的核心命题</h2>
    <div class="quote-box">
        <strong>全息胚不是中医独有的哲学，而是生物体（包括生物医学系统、复杂适应系统、AI 系统）的普遍规律。</strong><br>
        —— 5000 年人类医学 + 6 大现代科学 + 张颖清 19 项理论 + 21 世纪 AI = 21 世纪统一医学
    </div>

    <h2>5. 编排结构（8 卷）</h2>
    <ul style="margin: 0.8em 0; padding-left: 1.5em;">
        <li><strong>卷一·历史溯源</strong>（6 章）—— 美索不达米亚 → 古埃及 → 古希腊罗马 → 阿拉伯 → 古印度 → 中医演变</li>
        <li><strong>卷二·民族医学</strong>（8 章）—— 全球 6 大洲 50+ 民族医学的全息胚实践</li>
        <li><strong>卷三·现代科学</strong>（7 章）—— 神经 + 分子 + 胚胎 + 信息论 + 物理 + NEI 网络 + PK/PD 严格性</li>
        <li><strong>卷四·张颖清全息胚理论</strong>（5 章）—— 19 项理论体系 + 1995 论战 + 21 世纪应用</li>
        <li><strong>卷五-卷六·物理基础 + 治疗大典</strong>（11 篇）—— 5.x + 6.x + 7.x 系列</li>
        <li><strong>卷八·HoloScan 2.0 项目管理</strong>（8 篇）—— 提纲 + agency + 章程 + WBS + BP + 招聘 + 哲学</li>
    </ul>

    <h2>6. 编辑说明</h2>
    <p>本专著由 AI（基于 minimax 模型）辅助整理，用户（项目主导者）主导。AI 贡献研究、写作、整合；用户贡献方向、决策、临床经验。所有引用都标注了原始作者和年份，遵循学术诚信原则。</p>
    <p>本专著的中文版和英文版将分开发行。中文版保留 AI 整理 + 用户主编的模式；英文版将邀请国际学者共同编辑。</p>

    <div class="signature">
        <p>用户（项目主导者）<br>2026 年 7 月 3 日 · 厦门</p>
    </div>
</div>
""")

    # =================== 目录 ===================
    parts.append('<div class="toc"><h1>目 录</h1>')

    chapters = {
        "卷一·历史溯源": [
            ("第一章", "美索不达米亚医学的曙光", "8.6"),
            ("第二章", "古埃及医学体系", "8.7"),
            ("第三章", "古希腊罗马医学", "8.11"),
            ("第四章", "阿拉伯医学的黄金时代", "8.13"),
            ("第五章", "古印度医学体系", "8.14"),
            ("第六章", "中医的形成与演变", "8.15"),
        ],
        "卷二·民族医学与自然疗法": [
            ("第七章", "东亚传统医学", "8.16"),
            ("第八章", "藏医学与高原医学", "8.17"),
            ("第九章", "东南亚传统医学", "8.18"),
            ("第十章", "北美原住民医学", "8.19"),
            ("第十一章", "中南美洲传统医学", "8.20"),
            ("第十二章", "非洲传统医学", "8.21"),
            ("第十三章", "西伯利亚/蒙古/北极", "8.22"),
            ("第十四章", "澳洲与太平洋岛屿", "8.23"),
        ],
        "卷三·现代科学基础": [
            ("第十五章", "神经解剖学与全息", "8.24"),
            ("第十六章", "分子生物学与全息", "8.25"),
            ("第十七章", "胚胎学与全息", "8.26"),
            ("第十八章", "信息论与全息", "8.27"),
            ("第十九章", "物理学与全息", "8.28"),
            ("第二十章", "神经-内分泌-免疫网络", "8.29"),
            ("第廿一章", "生物动力学与药物代谢", "8.30"),
        ],
        "卷四·张颖清全息胚理论": [
            ("第廿二章", "张颖清学术生涯与全集", "8.31"),
            ("第廿三章", "9 大核心理论深度展开", "8.32"),
            ("第廿四章", "10 项扩展理论 + 现代反思", "8.33"),
            ("第廿五章", "21 世纪应用（收官）", "8.34"),
        ],
    }

    for vol_idx, vol_tuple in enumerate(VOLUMES):
        pdf_file, vol_full_name, vol_desc, vol_meta = vol_tuple
        if vol_idx < 4:
            chapters_in_vol = chapters.get(vol_full_name, [])
        else:
            chapters_in_vol = []

        parts.append(f'<div class="vol">')
        parts.append(f'<div class="vol-title">{vol_full_name}</div>')
        parts.append(f'<div class="vol-subtitle">{vol_desc}</div>')
        parts.append(f'<div class="vol-meta">{vol_meta} · 源文件: {pdf_file}</div>')
        if chapters_in_vol:
            parts.append('<div class="chapter-list">')
            for ch_num, ch_title, ch_file in chapters_in_vol:
                parts.append(f'<div><span class="ch-num">{ch_num}</span>{ch_title} <span style="color:#868e96; font-size:9pt;">[{ch_file}]</span></div>')
            parts.append('</div>')
        parts.append('</div>')

    # 后续卷
    parts.append("""
<div class="vol">
    <div class="vol-title">卷五-卷六·物理基础 + 治疗大典</div>
    <div class="vol-subtitle">5.x + 6.x + 7.x 系列 · 知识扩展 + 物理学基础 + 治疗大典</div>
    <div class="vol-meta">11 篇 · 源文件: vol5_6_foundation.pdf + vol7_therapies.pdf</div>
    <div class="chapter-list">
        <div><span class="ch-num">5.x</span>知识扩展系列（EEG / 舌诊 / 脉诊）</div>
        <div><span class="ch-num">6.x</span>物理学基础（DNA / Shannon / 神经节段 / HoloScan 2.0 / 突变 / 类器官）</div>
        <div><span class="ch-num">7.x</span>全息胚疗法家族（60+ 跨文化疗法 + 现代医学全息 + 跨文化对照 + 前沿方向 + AI Agent 全息）</div>
    </div>
</div>

<div class="vol">
    <div class="vol-title">卷八·HoloScan 2.0 项目管理 + 哲学 + 插图</div>
    <div class="vol-subtitle">8.0-8.5 项目管理 + 8.10 插图 + 8.12 哲学</div>
    <div class="vol-meta">10 篇 · 源文件: vol8_holoscan.pdf + vol8_philosophy.pdf + vol_image_prompts.pdf</div>
    <div class="chapter-list">
        <div><span class="ch-num">8.0</span>1000 页专著提纲</div>
        <div><span class="ch-num">8.1</span>HoloScan 2.0 agency-agents 规划</div>
        <div><span class="ch-num">8.2</span>项目章程（正式版）</div>
        <div><span class="ch-num">8.3</span>详细 WBS（300+ 任务）</div>
        <div><span class="ch-num">8.4</span>投资人 BP（20 页）</div>
        <div><span class="ch-num">8.5</span>50 岗位招聘计划</div>
        <div><span class="ch-num">8.10</span>古代医学插图 Prompt（20 张中英双语）</div>
        <div><span class="ch-num">8.12</span>全息胚本体论（多本体论协同）</div>
    </div>
</div>

<div class="vol">
    <div class="vol-title">附录·主项目 + HAIS</div>
    <div class="vol-subtitle">科普文章 + HAIS v0.1 + 财税调研</div>
    <div class="vol-meta">3 篇 · 源文件: main_summary.pdf</div>
    <div class="chapter-list">
        <div>《张颖清全息生物学 30 年》科普文章</div>
        <div>HAIS v0.1（HoloAgent Interface Standard）</div>
        <div>企业财税 Skills 调研报告</div>
    </div>
</div>
""")

    parts.append('</div>')

    # =================== 编辑信息 ===================
    parts.append("""
<div class="editor-info">
    <h1>编辑信息 / Editorial Information</h1>

    <h2>主编</h2>
    <p>用户（项目主导者）</p>
    <p>位置：厦门 | 时间：2026 年 7 月 3 日</p>

    <h2>AI 辅助</h2>
    <p>模型：minimax 系列（MiniMax-M2.7 / M3）</p>
    <p>工作流：OpenClaw 2026.6.10</p>
    <p>角色：研究助手 + 文档整理 + 初稿撰写 + 整合编辑</p>
    <p>注：AI 不作为原作者或学术权威，所有内容仍需读者独立判断和验证。</p>

    <h2>原始作者与文献</h2>
    <p>本专著引用了大量原始作者的研究工作，核心包括（按章节顺序）：</p>
    <table>
        <thead>
            <tr><th>章节</th><th>核心原作者 / 文献</th><th>时间</th></tr>
        </thead>
        <tbody>
            <tr><td>第一章 美索不达米亚</td><td>Biggs, R.D.; Scurlock, J.A.; Geller, M.J.</td><td>1969-2010</td></tr>
            <tr><td>第二章 古埃及</td><td>Breasted, J.H.; Ebbell, B.; Nunn, J.F.</td><td>1930-1996</td></tr>
            <tr><td>第三章 古希腊罗马</td><td>Hippocrates; Galen; Dioscorides; Pliny</td><td>~400 BCE-77 CE</td></tr>
            <tr><td>第四章 阿拉伯</td><td>Avicenna; Rhazes; Avenzoar; Maimonides</td><td>865-1204 CE</td></tr>
            <tr><td>第五章 古印度</td><td>Charaka; Sushruta; Atharva Veda</td><td>~1500-300 BCE</td></tr>
            <tr><td>第六章 中医</td><td>《黄帝内经》; 《伤寒论》; 李时珍; 张颖清</td><td>~200 BCE-2004 CE</td></tr>
            <tr><td>第七-十四章 民族医学</td><td>跨 6 大洲 50+ 民族医学</td><td>现代</td></tr>
            <tr><td>第十五章 神经解剖</td><td>Waxman, S.G.; Head, H.; Travell, J.</td><td>1893-2020</td></tr>
            <tr><td>第十六章 分子生物学</td><td>Watson & Crick; Yamanaka, S.; Clevers, H.</td><td>1953-2020</td></tr>
            <tr><td>第十七章 胚胎学</td><td>Lewis, E.B.; Tabin, C.; Gilbert, S.F.</td><td>1978-2020</td></tr>
            <tr><td>第十八章 信息论</td><td>Shannon, C.E.</td><td>1948</td></tr>
            <tr><td>第十九章 物理学</td><td>Gabor, D.; 't Hooft, G.; Susskind, L.</td><td>1947-1995</td></tr>
            <tr><td>第二十章 NEI 网络</td><td>Felten, D.; Blalock, E.; Pert, C.</td><td>1977-1985</td></tr>
            <tr><td>第廿一章 PK/PD</td><td>屠呦呦; Wagner, J.G.; Rowland, M.</td><td>2015-现代</td></tr>
            <tr><td>第廿二-廿五章 张颖清</td><td>张颖清本人; 张秀勤; 邹承鲁</td><td>1947-2004</td></tr>
        </tbody>
    </table>

    <h2>引用规范</h2>
    <p>本专著采用括号内联引用 + 章节末尾参考文献的双重引用规范：</p>
    <ul>
        <li><strong>内联引用</strong>：在正文中以（来源: 作者 年份, 作品）形式注明关键事实的原始出处。</li>
        <li><strong>参考文献</strong>：每个章节末尾列出该章节使用的全部原始文献。</li>
        <li><strong>AI 整理内容</strong>：跨章节综合分析、Mermaid 图、商业构想、AI Agent 架构等由 AI 整理者原创贡献，已在各文档开头明确标注。</li>
    </ul>

    <h2>版权与使用</h2>
    <p>本专著的 AI 整理部分采用 <strong>CC BY-NC-SA 4.0</strong> 协议。原始作者的部分版权归原作者所有，请遵循相应版权规定。引用本专著时，请保留完整的原始作者归属。</p>

    <h2>反馈与勘误</h2>
    <p>由于本专著大部分内容由 AI 整理，难免存在错误。欢迎读者：</p>
    <ul>
        <li>指出事实错误（通过 GitHub Issue 或邮件）</li>
        <li>补充原始文献（特别是张颖清本人未发表的手稿）</li>
        <li>提供临床证据（特别是第二掌骨诊法、Su Jok 的临床数据）</li>
        <li>改进 PK/PD 严格性（特别是中药多成分 PK）</li>
    </ul>

    <h2>项目位置</h2>
    <p>D:\obsidian\Holographic-Biology\</p>
    <p>项目地址：HoloScan 2.0（2026+）实施中</p>

    <h2>总览</h2>
    <table>
        <thead>
            <tr><th>项目</th><th>数据</th></tr>
        </thead>
        <tbody>
            <tr><td>专著章节</td><td>26 章（卷一 6 + 卷二 8 + 卷三 7 + 卷四 5）</td></tr>
            <tr><td>总字数</td><td>~110,000 字</td></tr>
            <tr><td>8.x 文档</td><td>32 份 / ~590 KB</td></tr>
            <tr><td>PDF 体系</td><td>10 个独立 PDF + 1 合并 PDF</td></tr>
            <tr><td>合并 PDF 大小</td><td>~30-50 MB</td></tr>
            <tr><td>合并 PDF 页数</td><td>~600-800 页</td></tr>
        </tbody>
    </table>
</div>
""")

    parts.append("</body></html>")

    html = "\n".join(parts)
    TMP_HTML.write_text(html, encoding="utf-8")
    return TMP_HTML


def html_to_pdf(html_path: Path, pdf_path: Path):
    """Edge headless 渲染"""
    cmd = [
        str(EDGE),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--print-to-pdf=" + str(pdf_path),
        "--print-to-pdf-no-header",
        "file:///" + str(html_path).replace("\\", "/"),
    ]
    print(f"[Edge] {html_path.name} → {pdf_path.name}")
    r = subprocess.run(cmd, capture_output=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"Edge 失败: {r.stderr.decode('utf-8', errors='replace')[:500]}")
    print(f"[Edge] 完成: {pdf_path.name}")


def merge_pdfs(output_path: Path, inputs: list):
    """用 pypdf 合并 PDF"""
    from pypdf import PdfWriter

    writer = PdfWriter()
    for pdf_path in inputs:
        if not pdf_path.exists():
            print(f"  ⚠ 跳过不存在: {pdf_path}")
            continue
        print(f"  + {pdf_path.name} ({pdf_path.stat().st_size / 1024:.0f} KB)")
        writer.append(str(pdf_path))
    writer.write(str(output_path))
    print(f"\n✅ 合并完成: {output_path}")


def main():
    print("=" * 60)
    print("1000 页专著 PDF 合并器")
    print("封面 + 序言 + 目录 + 编辑信息 + 10 卷正文")
    print("=" * 60)

    # 1. 生成封面/序言/目录/编辑信息 PDF
    print("\n[1/3] 生成封面/序言/目录/编辑信息...")
    html_path = build_front_matter()
    print(f"  HTML: {html_path} ({html_path.stat().st_size / 1024:.0f} KB)")
    html_to_pdf(html_path, FRONT_PDF)
    print(f"  PDF: {FRONT_PDF} ({FRONT_PDF.stat().st_size / 1024:.0f} KB)")

    # 2. 合并 11 个 PDF（1 个 front + 10 个卷）
    print("\n[2/3] 合并 PDF...")
    inputs = [FRONT_PDF]
    for pdf_file, _, _, _ in VOLUMES:
        inputs.append(BASE / pdf_file)

    merge_pdfs(OUTPUT, inputs)

    # 3. 验证
    print("\n[3/3] 验证输出...")
    if OUTPUT.exists():
        from pypdf import PdfReader
        reader = PdfReader(str(OUTPUT))
        n_pages = len(reader.pages)
        size_mb = OUTPUT.stat().st_size / 1024 / 1024
        print(f"  → PDF: {OUTPUT}")
        print(f"  → 页数: {n_pages}")
        print(f"  → 大小: {size_mb:.2f} MB")
    else:
        print("  ✗ PDF 未生成")

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
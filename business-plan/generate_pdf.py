# -*- coding: utf-8 -*-
"""
generate_pdf.py - 把 business-plan 知识库整理成 PDF

设计：
- 封面页 (中文标题 + 副标题 + 日期 + 简介)
- 目录页 (TOC)
- 按主题分组的内容页:
  第一部分：理论框架 (HAIS + 科普文章)
  第二部分：应用转化 (商业 + Agent隐喻 + 课件)
  第三部分：HoloAgent 实现 (v0.1 + v0.2.6 + 2 个总结)
- 用 Edge headless 打印 HTML → PDF

用法:
    python generate_pdf.py
"""
import datetime
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension

BASE = Path(r"D:\obsidian\Holographic-Biology\business-plan")
HTML_OUT = Path(r"D:\temp\business_plan_book.html")
PDF_OUT = BASE / "business-plan-book.pdf"

# Edge 路径
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

# ============================================================
# 内容分组与顺序
# ============================================================
SECTIONS = [
    ("第零部分  双源汇流", [
        ("0.0-dual-source-confluence.md", "东西方全息思想的平行发现与 laimengjun 的统一", "开篇论述"),
    ]),
    ("第一部分  理论框架", [
        ("00-skills-for-finance-tax.md", "企业财税分析 Skills 调研报告", "Skills调研"),
        ("5.0-knowledge-expansion-summary.md", "全息生物学知识扩展（5.x 系列）", "知识扩展"),
        ("6.0-physics-foundations-summary.md", "全息生物学物理学基础（6.x 系列）", "物理基础"),
        ("7.x-application-expansion-summary.md", "全息胚疗法家族总览（7.x 系列）", "应用扩展"),
        ("7.0-tcm-holography-overview.md", "全息胚疗法家族 总览与知识图谱", "总览"),
        ("7.1-tcm-natural-therapies-mapping.md", "TCM/自然疗法映射（63 种）", "疗法映射"),
        ("7.2-modern-medicine-holography.md", "现代医学的全息现象", "现代医学"),
        ("7.3-cross-cultural-comparison.md", "跨文化传统医学全息对照", "跨文化"),
        ("7.4-frontier-directions.md", "全息胚疗法的前沿方向", "前沿"),
        ("7.5-ai-agent-holography.md", "AI Agent 全息架构（HAIS 理论根源）", "数字全息胚"),
        ("8.0-monograph-1000p-outline.md", "1000 页专著提纲", "专著"),
        ("8.1-holoscan-2.0-agency-plan.md", "HoloScan 2.0 项目 · agency-agents 规划", "项目管理"),
        ("8.2-holoscan-2.0-project-charter.md", "HoloScan 2.0 项目章程（正式版）", "项目章程"),
        ("8.3-holoscan-2.0-detailed-wbs.md", "HoloScan 2.0 详细 WBS（300+ 任务）", "WBS"),
        ("8.4-holoscan-2.0-investor-bp.md", "HoloScan 2.0 投资人 BP（20 页）", "BP"),
        ("8.5-holoscan-2.0-team-recruitment.md", "HoloScan 2.0 50 岗位招聘计划", "招聘"),
        ("8.6-monograph-vol1-ch1-mesopotamia.md", "专著·卷一第一章·美索不达米亚医学", "专著·历史"),
        ("8.7-monograph-vol1-ch2-egypt.md", "专著·卷一第二章·古埃及医学", "专著·历史"),
        ("8.8-hais-v0.2-design.md", "HAIS v0.2 设计文档（记忆隔离 + 跨 Agent 消息总线）", "HAIS v0.2"),
        ("8.9-holoagent-v1.0-design.md", "HoloAgent v1.0 升级设计", "HoloAgent v1.0"),
        ("8.10-image-prompts-ancient-medicine.md", "古代医学插图 Prompt 文档（20 张）", "插图 Prompt"),
        ("8.11-monograph-vol1-ch3-greece-rome.md", "专著·卷一第三章·古希腊罗马医学", "专著·历史"),
        ("8.12-holographic-embryo-ontology.md", "专著·卷八第四十一章·全息胚本体论（哲学）", "专著·哲学"),
        ("HAIS-v0.1.md", "HoloAgent Interface Standard (HAIS v0.1)", "标准"),
        ("科普文章-张颖清全息生物学30年.md", "张颖清全息生物学 30 年（科普）", "科普"),
    ]),
    ("第二部分  应用转化", [
        ("4.2-commercial-idea.md", "HoloScan 商业构想 (v0.1)", "商业"),
        ("4.3-agent-metaphor.md", "全息生物学作为 AI Agent 架构隐喻", "隐喻"),
        ("4.4-course-materials.md", "跨学科课件设计（16 周）", "课件"),
        ("4.5-30-ep-short-video-course.md", "30 集短视频课程设计", "课程"),
        ("4.5.1-30-ep-scripts.md", "30 集短视频课程脚本（完整）", "脚本"),
    ]),
    ("第三部分  HoloAgent 实现", [
        ("holo_agent_prototype.py", "HoloAgent 原型 v0.1（参考实现）", "代码"),
        ("holo_agent_v0.2.py", "HoloAgent 生产化版本 v0.2.6", "代码"),
        ("4.3-prototype-summary.md", "v0.1 原型测试报告", "报告"),
        ("holo_agent_v0.2_summary.md", "v0.2.6 生产化总结（含完整调试历程）", "报告"),
    ]),
    ("第四部分  数学基础系列 (8.x)", [
        ("8.0-core-forward-inverse-framework.md", "全息生物学的基因-贝叶斯基石：正向-反向推理框架", "数学"),
        ("8.1-bayesian-gene-error-foundation.md", "贝叶斯全息理论：从基因复制到诊断精度", "数学"),
        ("8.2-dev-holographic-mapping-formation.md", "发育全息映射：从受精卵到体表对应", "数学"),
        ("8.3-bci-invasive-non-invasive-comparison.md", "BCI 精度对比：非侵入 vs 侵入", "数学"),
        ("8.4-multimodal-sensor-fusion.md", "多模态贝叶斯融合策略", "数学"),
        ("8.5-monte-carlo-simulation.md", "蒙特卡洛仿真：50 万患者精度验证", "数学"),
        ("8.6-time-series-signal-analysis.md", "时序信号与非线性动力学分析", "数学"),
        ("8.7-sensor-engineering-design.md", "传感器工程设计：HoloScan 2.0 硬件", "数学"),
    ]),
]


def md_to_html(md_text: str, code_lang_default: str = "python") -> str:
    """Markdown 转 HTML（带代码高亮 + TOC）"""
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "toc",
            CodeHiliteExtension(noclasses=True, guess_lang=False),
        ],
        extension_configs={
            "fenced_code": {"lang_prefix": "language-"},
        },
    )
    return md.convert(md_text)


def py_to_html(py_text: str) -> str:
    """Python 文件转 HTML（带语法高亮）"""
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            CodeHiliteExtension(noclasses=True),
        ],
    )
    # 用 markdown 包一层 (会变成代码块带高亮)
    return md.convert(f"```python\n{py_text}\n```")


def collect_section(file_name: str, title: str, kind: str) -> tuple[str, str, str]:
    """读单个文件, 转 HTML, 返回 (anchor, title, html)"""
    p = BASE / file_name
    if not p.exists():
        return file_name, title, f'<p style="color:red">⚠ 文件不存在: {file_name}</p>'
    text = p.read_text(encoding="utf-8")
    if kind == "代码" or file_name.endswith(".py"):
        html = py_to_html(text)
    else:
        html = md_to_html(text)
    return file_name, title, html


# ============================================================
# HTML 模板
# ============================================================
CSS = """
<style>
@page {
    size: A4;
    margin: 2cm 1.8cm 2.2cm 1.8cm;
    @top-center {
        content: "全息生物学商业化与 HoloAgent 框架 · 2026";
        font-size: 9pt;
        color: #666;
    }
    @bottom-center {
        content: "Page " counter(page) " / " counter(pages);
        font-size: 9pt;
        color: #666;
    }
}

@page :first {
    @top-center { content: ""; }
    @bottom-center { content: ""; }
    margin: 0;
}

body {
    font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei",
                 "Helvetica Neue", Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.6;
    color: #222;
    max-width: 100%;
    margin: 0;
    padding: 0;
}

/* 封面 */
.cover {
    page-break-after: always;
    height: 26cm;
    padding: 4cm 2cm 2cm 2cm;
    text-align: center;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    position: relative;
}
.cover h1 {
    font-size: 32pt;
    color: #c92a2a;
    margin: 0 0 0.5cm 0;
    letter-spacing: 0.1em;
}
.cover h2 {
    font-size: 16pt;
    color: #495057;
    font-weight: normal;
    margin: 0 0 3cm 0;
    letter-spacing: 0.05em;
}
.cover .meta {
    margin-top: 6cm;
    font-size: 11pt;
    color: #495057;
    line-height: 2;
}
.cover .meta strong { color: #c92a2a; }
.cover .footer {
    position: absolute;
    bottom: 2cm;
    left: 0; right: 0;
    text-align: center;
    font-size: 9pt;
    color: #868e96;
}

/* 目录 */
.toc {
    page-break-after: always;
    padding: 1.5cm 0;
}
.toc h1 {
    font-size: 20pt;
    color: #c92a2a;
    border-bottom: 3px solid #c92a2a;
    padding-bottom: 0.3cm;
    margin-bottom: 0.8cm;
}
.toc ul {
    list-style: none;
    padding: 0;
}
.toc li {
    padding: 0.3em 0;
    font-size: 11pt;
    border-bottom: 1px dotted #dee2e6;
}
.toc li.lv1 { font-weight: bold; padding-left: 0; margin-top: 0.5em; color: #c92a2a; }
.toc li.lv2 { padding-left: 1.5em; color: #495057; }
.toc a { color: inherit; text-decoration: none; }

/* 分组 */
.section-group {
    page-break-before: always;
    margin-top: 0;
}
.section-group > h1 {
    font-size: 22pt;
    color: #c92a2a;
    border-bottom: 4px solid #c92a2a;
    padding-bottom: 0.3cm;
    margin: 0 0 0.5cm 0;
}

/* 单个文档 */
.doc {
    page-break-before: always;
    padding-top: 0;
}
.doc > h1.doc-title {
    font-size: 16pt;
    color: #fff;
    background: #495057;
    padding: 0.4cm 0.6cm;
    margin: 0 0 0.5cm 0;
    border-left: 0.4cm solid #c92a2a;
}

/* Markdown 渲染元素 */
h1 { font-size: 14pt; color: #c92a2a; border-bottom: 2px solid #dee2e6; padding-bottom: 0.2cm; }
h2 { font-size: 12pt; color: #495057; margin-top: 0.8cm; }
h3 { font-size: 11pt; color: #495057; }
p { margin: 0.5em 0; text-align: justify; }
ul, ol { margin: 0.5em 0; padding-left: 1.5em; }
li { margin: 0.2em 0; }
code {
    font-family: "Cascadia Code", "Fira Code", Consolas, "Liberation Mono", monospace;
    font-size: 9.5pt;
    background: #f1f3f5;
    padding: 0.1em 0.3em;
    border-radius: 2px;
    color: #c92a2a;
}
pre {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-left: 3px solid #495057;
    padding: 0.5em 0.8em;
    overflow-x: auto;
    border-radius: 3px;
    margin: 0.5em 0;
    font-size: 9pt;
    line-height: 1.45;
}
pre code {
    background: transparent;
    padding: 0;
    color: #212529;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.8em 0;
    font-size: 9.5pt;
}
th, td {
    border: 1px solid #adb5bd;
    padding: 0.3em 0.6em;
    text-align: left;
}
th {
    background: #e9ecef;
    font-weight: bold;
}
blockquote {
    border-left: 4px solid #c92a2a;
    margin: 0.8em 0;
    padding: 0.3em 1em;
    background: #fff5f5;
    color: #495057;
}
hr {
    border: none;
    border-top: 1px solid #adb5bd;
    margin: 1em 0;
}
</style>
"""


def build_cover() -> str:
    today = datetime.date.today().strftime("%Y 年 %m 月 %d 日")
    return f"""
<div class="cover">
    <h1>全息生物学商业化</h1>
    <h1>&</h1>
    <h1>HoloAgent 框架</h1>
    <h2>laimengjun 统一框架 · 东西方平行史 · 8.x 数学基础</h2>
    <div class="meta">
        <p><strong>主题</strong>  张颖清"全息生物学"的现代诠释 + AI Agent 架构映射 + 全息胚疗法家族</p>
        <p><strong>范围</strong>  张颖清全息胚理论 / Bohm-Pribram 全息脑 / Goldberger 分形生理学 / Haken-Prigogine 自组织 / 8.x 数学基础 / HoloScan 2.0 工程方案</p>
        <p><strong>文件数</strong>  25+ 个 (.md + .py, 共 ~700 KB, 17 万余字)</p>
        <p><strong>汇编日期</strong>  {today}</p>
    </div>
    <div class="footer">
        AI 辅助整理 · 基于 OpenClaw 工作流 · 厦门
    </div>
</div>
"""


def build_editor_note() -> str:
    """编者按页 — 明确说明整理者、AI 角色、原始作者、引用规范"""
    return """
<div class="editor-note" style="page-break-after: always; padding: 1.5cm 1cm;">
    <h1 style="font-size: 18pt; color: #c92a2a; border-bottom: 3px solid #c92a2a; padding-bottom: 0.3cm; margin-bottom: 0.8cm;">
        编者按 / Editorial Note
    </h1>

    <h2 style="font-size: 13pt; color: #495057; margin-top: 0.5cm;">一、本书性质</h2>
    <p>本书是<strong>以张颖清"全息生物学"为核心的跨学科研究资料汇编</strong>，不是张颖清本人的原著，也不是任何医学院校的教材。本书的目的是为研究张颖清学派、AI Agent 架构、全息胚疗法家族提供一份<strong>可追溯、可验证、可工程化</strong>的参考文档。</p>

    <h2 style="font-size: 13pt; color: #495057; margin-top: 0.5cm;">二、整理者与 AI 角色</h2>
    <ul>
        <li><strong>项目负责人</strong>：用户本人（位置：厦门）</li>
        <li><strong>AI 整理者</strong>：基于 MiniMax 系列模型（minimax/MiniMax-M2.7 / M3）</li>
        <li><strong>AI 工作流</strong>：基于 OpenClaw 2026.6.10</li>
        <li><strong>AI 角色</strong>：研究助手、文档整理者、初稿撰写者；<strong>不是</strong>原作者，也不是学术权威。所有内容仍需读者独立判断和验证。</li>
    </ul>

    <h2 style="font-size: 13pt; color: #495057; margin-top: 0.5cm;">三、核心原作者与原始文献</h2>
    <p>本书引用了大量原创作者的研究工作。完整列表见各章节末尾"参考文献"部分。核心原作者包括：</p>
    <ul>
        <li><strong>张颖清</strong>（1947-2004，山东大学全息生物学研究所）：全息胚理论创始人，《生物全息诊疗法》（1985）、《全息生物学概论》（1993）</li>
        <li><strong>张秀勤</strong>（2006）：《全息经络刮痧法》专著作者，张颖清 → 现代中医临床的关键中介</li>
        <li><strong>Henry Head</strong>（1861-1940）：1893 年发现 Head's Zones（内脏-体表痛觉过敏带），发表 <em>On disturbances of sensation</em>（<em>Brain</em>）</li>
        <li><strong>James Mackenzie</strong>（1853-1925）：1909 年《Symptoms and their interpretation》</li>
        <li><strong>Janet Travell</strong>（1901-1997）：Trigger Point（肌筋膜触发点）发现者，与 Simons 合著《Myofascial Pain and Dysfunction》</li>
        <li><strong>Stephen Waxman</strong>：现代《Clinical Neuroanatomy》（McGraw-Hill）作者</li>
        <li><strong>William Fitzgerald</strong>（1872-1942）：1913 年 Zone Therapy 创始人</li>
        <li><strong>Eunice Ingham</strong>（1889-1974）：1938 年《Stories the Feet Can Tell》，Reflexology 之母</li>
        <li><strong>Paul Nogier</strong>（1908-1996）：1957 年 Auriculotherapy 系统化</li>
        <li><strong>Park Jae Woo</strong>（朴杰午，1942-2010）：1980s Su Jok 手足针创始人</li>
        <li><strong>Tae-Woo Yoo</strong>（柳泰午）：1975 年 Korean Hand Acupuncture 创始人</li>
        <li><strong>焦顺发</strong>（1939- ）：1971 年头皮针（焦氏）创始人</li>
        <li><strong>山本</strong>（Yamamoto）：1973 年 YNSA 山本头皮针创始人</li>
        <li><strong>彭静山</strong>（1909-2003）：1970s 眼针创始人</li>
        <li><strong>张心曙</strong>：1970s 腕踝针创始人</li>
        <li><strong>薄智云</strong>：1990s 腹针创始人</li>
        <li><strong>符仲华</strong>：1996 浮针创始人</li>
        <li><strong>朱汉章</strong>（1929-2006）：1976 针刀创始人</li>
        <li><strong>George Goodheart</strong>（1918-2008）：1964 应用肌动学创始人</li>
        <li><strong>Reinhold Voll</strong>（1909-1989）：1950s Voll 电针（EAV）创始人</li>
        <li><strong>宇妥·元丹贡布</strong>（708-833）：8 世纪《四部医典》藏医奠基人</li>
        <li><strong>李济马</strong>（1837-1900）：1894《东医寿世保元》四象医学创始人</li>
        <li><strong>阿维森纳</strong>（Avicenna, 980-1037）：1025 年《医典》Unani 医学奠基人</li>
        <li><strong>廖育群</strong>（现代）：2008《阿育吠陀——印度传统医学》北京大学医学出版社</li>
        <li><strong>Karl Pribram</strong>（1919-2015）：1971《Languages of the Brain》全息脑理论</li>
    </ul>

    <h2 style="font-size: 13pt; color: #495057; margin-top: 0.5cm;">四、引用规范</h2>
    <p>本书采用<strong>括号内联引用 + 章节末尾参考文献</strong>的双重引用规范：</p>
    <ul>
        <li><strong>内联引用</strong>：在正文中以（来源: 作者 年份, 作品）形式注明关键事实的原始出处。</li>
        <li><strong>参考文献</strong>：每个章节末尾列出该章节使用的全部原始文献。</li>
        <li><strong>AI 整理内容</strong>：跨章节综合分析、Mermaid 图、商业构想、AI Agent 架构等由 AI 整理者原创贡献，已在各文档开头明确标注。</li>
    </ul>

    <h2 style="font-size: 13pt; color: #495057; margin-top: 0.5cm;">五、版权与使用</h2>
    <p>本书整理者贡献的部分采用 <strong>CC BY-NC-SA 4.0</strong> 协议。原始作者的部分版权归原作者所有，请遵循相应版权规定。引用本书时，请保留完整的原始作者归属。</p>

    <h2 style="font-size: 13pt; color: #495057; margin-top: 0.5cm;">六、反馈与勘误</h2>
    <p>由于本书大部分内容由 AI 整理，<strong>难免存在错误</strong>。欢迎读者：</p>
    <ul>
        <li>指出事实错误（通过"GitHub Issue"或邮件）</li>
        <li>补充原始文献（特别是张颖清本人未发表的手稿）</li>
        <li>提供临床证据（特别是第二掌骨诊法、Su Jok 的临床数据）</li>
    </ul>

    <p style="margin-top: 1cm; padding: 0.5cm; background: #fff5f5; border-left: 4px solid #c92a2a;">
        <strong>📌 阅读建议</strong>：建议从第一部分"理论框架"开始阅读，理解张颖清全息胚理论的核心；第二部分"应用转化"了解 5 类核心应用 + 30 集短视频课程；第三部分"HoloAgent 实现"了解 AI Agent 全息架构。本书 7.x 系列（位于第一部分）建立了全息胚疗法家族的完整应用框架。
    </p>
</div>
"""


def build_toc() -> str:
    """构建 TOC HTML (手动生成, 不依赖 markdown.toc 自动)"""
    items = []
    for group_name, files in SECTIONS:
        items.append(f'<li class="lv1"><a href="#group-{len(items)}">{group_name}</a></li>')
        for fname, title, kind in files:
            items.append(f'<li class="lv2"><a href="#doc-{fname}">· {title}</a> <span style="color:#adb5bd;font-size:9pt">[{kind}]</span></li>')
    return f"""
<div class="toc">
    <h1>目录</h1>
    <ul>
        {chr(10).join(items)}
    </ul>
</div>
"""


def build_book() -> str:
    parts = [build_cover(), build_editor_note(), build_toc()]

    # 收集每个分组的 HTML
    for g_idx, (group_name, files) in enumerate(SECTIONS):
        group_html = [f'<div class="section-group"><h1 id="group-{g_idx}">{group_name}</h1>']
        for fname, title, kind in files:
            _, _, html = collect_section(fname, title, kind)
            group_html.append(
                f'<div class="doc" id="doc-{fname}">'
                f'<h1 class="doc-title">{title} <span style="float:right;font-size:9pt;font-weight:normal;color:#ced4da">[{kind}]</span></h1>'
                f'{html}'
                f'</div>'
            )
        group_html.append('</div>')
        parts.append("\n".join(group_html))

    body = "\n".join(parts)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>全息生物学商业化 & HoloAgent 框架</title>
    {CSS}
</head>
<body>
{body}
</body>
</html>
"""


def html_to_pdf_via_edge(html_path: Path, pdf_path: Path):
    """用 Edge headless 打印 HTML 为 PDF"""
    cmd = [
        str(EDGE),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--print-to-pdf=" + str(pdf_path),
        "--print-to-pdf-no-header",
        "file:///" + str(html_path).replace("\\", "/"),
    ]
    print(f"[Edge] {' '.join(cmd[:6])} ...")
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    if r.returncode != 0:
        print(f"Edge stderr: {r.stderr.decode('utf-8', errors='replace')[:500]}")
        raise RuntimeError(f"Edge 退出码 {r.returncode}")
    print(f"[Edge] 完成, PDF: {pdf_path}")


def main():
    print("=" * 60)
    print("Business-Plan → PDF 生成器")
    print("=" * 60)

    # 1. 构建 HTML
    print("\n[1/3] 构建 HTML ...")
    html = build_book()
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"  → HTML: {HTML_OUT} ({len(html):,} chars)")

    # 2. Edge 打印 PDF
    print("\n[2/3] Edge headless 打印 PDF ...")
    t0 = time.time()
    html_to_pdf_via_edge(HTML_OUT, PDF_OUT)
    print(f"  → 用时: {time.time() - t0:.1f}s")

    # 3. 验证
    print("\n[3/3] 验证输出 ...")
    if PDF_OUT.exists():
        size_kb = PDF_OUT.stat().st_size / 1024
        print(f"  → PDF: {PDF_OUT} ({size_kb:.1f} KB)")
    else:
        print(f"  ✗ PDF 未生成")

    print("\n完成。")


if __name__ == "__main__":
    main()
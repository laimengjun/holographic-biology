# -*- coding: utf-8 -*-
"""
生成多个 PDF（拆分版本）
- 避免单次 Edge headless 超时
- 按"卷/系列"拆分
- 用户可独立访问每个 PDF
"""
import datetime
import os
import subprocess
import sys
import time
from pathlib import Path
from pathlib import Path

# UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')

# 路径
BASE = Path(r"D:\obsidian\Holographic-Biology\business-plan")
HTML_DIR = Path(r"D:\temp")
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

# 按系列拆分
SPLITS = [
    ("vol1_history", "卷一·历史溯源", [
        ("8.6-monograph-vol1-ch1-mesopotamia.md", "第一章·美索不达米亚医学", "历史"),
        ("8.7-monograph-vol1-ch2-egypt.md", "第二章·古埃及医学", "历史"),
        ("8.11-monograph-vol1-ch3-greece-rome.md", "第三章·古希腊罗马医学", "历史"),
        ("8.13-monograph-vol1-ch4-arabic.md", "第四章·阿拉伯黄金时代", "历史"),
        ("8.14-monograph-vol1-ch5-india.md", "第五章·古印度医学", "历史"),
        ("8.15-monograph-vol1-ch6-tcm.md", "第六章·中医演变", "历史"),
    ]),
    ("vol2_ethnic", "卷二·民族医学与自然疗法", [
        ("8.16-monograph-vol2-ch7-east-asia.md", "第七章·东亚传统医学", "民族"),
        ("8.17-monograph-vol2-ch8-tibet-mongolia.md", "第八章·藏医与高原医学", "民族"),
        ("8.18-monograph-vol2-ch9-southeast-asia.md", "第九章·东南亚传统医学", "民族"),
        ("8.19-monograph-vol2-ch10-north-america.md", "第十章·北美原住民医学", "民族"),
        ("8.20-monograph-vol2-ch11-latin-america.md", "第十一章·中南美洲传统医学", "民族"),
        ("8.21-monograph-vol2-ch12-africa.md", "第十二章·非洲传统医学", "民族"),
        ("8.22-monograph-vol2-ch13-arctic.md", "第十三章·西伯利亚/极地", "民族"),
        ("8.23-monograph-vol2-ch14-oceania.md", "第十四章·澳洲/太平洋", "民族"),
    ]),
    ("vol5_therapies", "卷五·治疗大典（4 章）", [
        ("8.35-monograph-vol5-ch26-acupoint-atlas.md", "第二十六章·全身穴位全息胚图谱", "治疗"),
        ("8.36-monograph-vol5-ch27-tcm-therapies.md", "第二十七章·治疗大典：传统中医类", "治疗"),
        ("8.37-monograph-vol5-ch28-modern-therapies.md", "第二十八章·治疗大典：现代类", "治疗"),
        ("8.38-monograph-vol5-ch29-cross-cultural-therapies.md", "第二十九章·治疗大典：跨文化类", "治疗"),
    ]),
    ("vol6_holoscan_eng", "卷六·HoloScan 2.0 工程实现（4 章）", [
        ("8.39-monograph-vol6-ch30-holoscan-design.md", "第三十章·HoloScan 2.0 总体设计", "工程"),
        ("8.40-monograph-vol6-ch31-hardware.md", "第三十一章·8 微系统硬件设计", "工程"),
        ("8.41-monograph-vol6-ch32-ai-software.md", "第三十二章·AI 软件栈", "工程"),
        ("8.42-monograph-vol6-ch33-regulatory.md", "第三十三章·监管与合规", "工程"),
    ]),
    ("vol7_clinical", "卷七·临床应用与验证（3 章）", [
        ("8.43-monograph-vol7-ch34-clinical-trials.md", "第三十四章·临床试验设计", "临床"),
        ("8.44-monograph-vol7-ch35-case-studies.md", "第三十五章·典型案例集", "临床"),
        ("8.45-monograph-vol7-ch36-killer-apps.md", "第三十六章·杀手级应用", "临床"),
    ]),
    ("vol8_holoscan", "卷八·HoloScan 2.0 项目管理", [
        ("8.0-monograph-1000p-outline.md", "1000 页专著提纲", "项目管理"),
        ("8.1-holoscan-2.0-agency-plan.md", "agency-agents 规划", "项目管理"),
        ("8.2-holoscan-2.0-project-charter.md", "项目章程（正式版）", "项目管理"),
        ("8.3-holoscan-2.0-detailed-wbs.md", "详细 WBS（300+ 任务）", "WBS"),
        ("8.4-holoscan-2.0-investor-bp.md", "投资人 BP（20 页）", "BP"),
        ("8.5-holoscan-2.0-team-recruitment.md", "50 岗位招聘计划", "招聘"),
        ("8.8-hais-v0.2-design.md", "HAIS v0.2 设计", "HAIS"),
        ("8.9-holoagent-v1.0-design.md", "HoloAgent v1.0 设计", "HoloAgent"),
    ]),
    ("vol8_philosophy", "卷八·哲学与全息胚本体论", [
        ("8.12-holographic-embryo-ontology.md", "全息胚本体论（关系·信息·实践）", "哲学"),
    ]),
    ("vol5_6_foundation", "卷五-卷六·物理基础 + 治疗大典", [
        ("6.0-physics-foundations-summary.md", "物理学基础（6.x 系列）", "物理"),
        ("6.1-dna-holographic-biology.md", "DNA 全息", "物理"),
        ("6.2-shannon-information-hologram.md", "Shannon 信息论", "物理"),
        ("6.3-neural-segment-micro-system.md", "神经节段", "物理"),
        ("6.4-holoscan-2-physics-implementation.md", "HoloScan 2.0 物理实现", "物理"),
        ("6.5-mutation-holographic-embryo.md", "突变与全息胚", "物理"),
        ("6.6-organoid-holographic-embryo.md", "类器官与全息胚", "物理"),
        ("5.0-knowledge-expansion-summary.md", "知识扩展（5.x 系列）", "知识扩展"),
        ("5.1-eeg-brain-computer-interface.md", "EEG 脑机接口", "知识扩展"),
        ("5.2-tongue-diagnosis-principles.md", "舌诊", "知识扩展"),
        ("5.3-pulse-diagnosis-tcm.md", "脉诊", "知识扩展"),
    ]),
    ("vol3_modern", "卷三·现代科学基础（7 章）", [
        ("8.24-monograph-vol3-ch15-neuroanatomy.md", "第十五章·神经解剖学与全息", "现代科学"),
        ("8.25-monograph-vol3-ch16-molecular.md", "第十六章·分子生物学与全息", "现代科学"),
        ("8.26-monograph-vol3-ch17-embryology.md", "第十七章·胚胎学与全息", "现代科学"),
        ("8.27-monograph-vol3-ch18-information.md", "第十八章·信息论与全息", "现代科学"),
        ("8.28-monograph-vol3-ch19-physics.md", "第十九章·物理学与全息", "现代科学"),
        ("8.29-monograph-vol3-ch20-nei.md", "第二十章·神经-内分泌-免疫网络", "现代科学"),
        ("8.30-monograph-vol3-ch21-biokinetics-pk.md", "第廿一章·生物动力学与药物代谢", "现代科学"),
    ]),
    ("vol4_zhang", "卷四·张颖清全息胚理论（5 章）", [
        ("8.31-monograph-vol4-ch22-zhang-life.md", "第廿二章·张颖清学术生涯", "张颖清"),
        ("8.32-monograph-vol4-ch23-core-theories.md", "第廿三章·9 大核心理论", "张颖清"),
        ("8.33-monograph-vol4-ch24-extended-theories.md", "第廿四章·10 项扩展理论", "张颖清"),
        ("8.34-monograph-vol4-ch25-future.md", "第廿五章·21 世纪应用（收官）", "张颖清"),
    ]),
    ("vol7_therapies", "卷七·全息胚疗法家族", [
        ("7.0-tcm-holography-overview.md", "总览 + 知识图谱", "总览"),
        ("7.1-tcm-natural-therapies-mapping.md", "TCM/自然疗法映射（63 种）", "疗法"),
        ("7.2-modern-medicine-holography.md", "现代医学全息现象", "现代医学"),
        ("7.3-cross-cultural-comparison.md", "跨文化传统医学对照", "跨文化"),
        ("7.4-frontier-directions.md", "前沿方向", "前沿"),
        ("7.5-ai-agent-holography.md", "AI Agent 全息架构", "AI"),
        ("7.x-application-expansion-summary.md", "7.x 系列总结", "总结"),
    ]),
    ("vol_image_prompts", "古代医学插图 Prompt 文档", [
        ("8.10-image-prompts-ancient-medicine.md", "20 张图片 Prompt（双语）", "插图"),
    ]),
    ("main_summary", "主项目 + HAIS", [
        ("科普文章-张颖清全息生物学30年.md", "张颖清全息生物学 30 年（科普）", "科普"),
        ("HAIS-v0.1.md", "HoloAgent Interface Standard (HAIS v0.1)", "HAIS"),
        ("00-skills-for-finance-tax.md", "企业财税 Skills 调研报告", "调研"),
    ]),
]


def collect_files_to_html(prefix: str, html_path: Path, sections: list) -> str:
    """合并多个 markdown 为单个 HTML"""
    import markdown
    from markdown.extensions.codehilite import CodeHiliteExtension
    from markdown.extensions.toc import TocExtension

    parts = [f"<!DOCTYPE html><html><head><meta charset='UTF-8'>"]
    parts.append(f"<title>{prefix}</title>")
    parts.append("""
<style>
@page { size: A4; margin: 2cm 1.8cm 2.2cm 1.8cm; }
body { font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; font-size: 10.5pt; line-height: 1.6; color: #222; }
h1 { font-size: 16pt; color: #c92a2a; border-bottom: 2px solid #dee2e6; padding-bottom: 0.2cm; }
h2 { font-size: 13pt; color: #495057; margin-top: 0.8cm; }
h3 { font-size: 11pt; color: #495057; }
.doc { page-break-before: always; }
.doc-title { background: #495057; color: #fff; padding: 0.4cm 0.6cm; margin-bottom: 0.5cm; }
pre { background: #f8f9fa; border-left: 3px solid #495057; padding: 0.5em 0.8em; font-size: 9pt; }
code { font-family: "Cascadia Code", Consolas, monospace; font-size: 9.5pt; background: #f1f3f5; padding: 0.1em 0.3em; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; }
th, td { border: 1px solid #adb5bd; padding: 0.3em 0.6em; }
th { background: #e9ecef; }
blockquote { border-left: 4px solid #c92a2a; margin: 0.8em 0; padding: 0.3em 1em; background: #fff5f5; }
</style>
</head><body>
""")
    parts.append(f"<h1 style='text-align:center; font-size:24pt'>{prefix}</h1>")

    for fname, title, kind in sections:
        fpath = BASE / fname
        if not fpath.exists():
            parts.append(f"<p style='color:red'>⚠ 文件不存在: {fname}</p>")
            continue
        text = fpath.read_text(encoding="utf-8")
        md = markdown.Markdown(extensions=[
            "fenced_code", "tables", "toc", "codehilite",
        ])
        html_content = md.convert(text)
        parts.append(f"<div class='doc'>")
        parts.append(f"<h1 class='doc-title'>{title} [{kind}]</h1>")
        parts.append(html_content)
        parts.append("</div>")

    parts.append("</body></html>")
    html = "\n".join(parts)
    html_path.write_text(html, encoding="utf-8")
    return html


def html_to_pdf_via_edge(html_path: Path, pdf_path: Path):
    """Edge headless HTML → PDF"""
    cmd = [
        str(EDGE),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--print-to-pdf=" + str(pdf_path),
        "--print-to-pdf-no-header",
        "file:///" + str(html_path).replace("\\", "/"),
    ]
    print(f"[Edge] {html_path.name} → {pdf_path.name} ...")
    r = subprocess.run(cmd, capture_output=True, timeout=300)
    if r.returncode != 0:
        err = r.stderr.decode('utf-8', errors='replace')[:500]
        raise RuntimeError(f"Edge 失败: {err}")
    print(f"[Edge] 完成: {pdf_path.name}")


def main():
    print("=" * 60)
    print("PDF 拆分生成器")
    print("=" * 60)

    for prefix, name, sections in SPLITS:
        print(f"\n[{prefix}] {name} ({len(sections)} 个文件)")

        html_path = HTML_DIR / f"{prefix}.html"
        pdf_path = BASE / f"{prefix}.pdf"

        # 1. 收集 HTML
        print(f"  [1/2] 生成 HTML ({len(sections)} 个文件)...")
        collect_files_to_html(name, html_path, sections)
        print(f"  → HTML: {html_path}")

        # 2. Edge → PDF
        print(f"  [2/2] Edge → PDF...")
        t0 = time.time()
        try:
            html_to_pdf_via_edge(html_path, pdf_path)
            elapsed = time.time() - t0
            if pdf_path.exists():
                size_kb = pdf_path.stat().st_size / 1024
                print(f"  → PDF: {pdf_path} ({size_kb:.1f} KB, {elapsed:.1f}s)")
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            continue

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
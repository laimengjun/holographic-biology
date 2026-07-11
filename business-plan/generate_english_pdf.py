# -*- coding: utf-8 -*-
"""
generate_english_pdf.py - English-only PDF of the holographic discovery monograph
Gibbon-style literary English, 15 chapters + epilogue
"""
import datetime, os, subprocess, time, json
from pathlib import Path
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension

BASE = Path(r"D:\obsidian\Holographic-Biology\business-plan")
HTML_OUT = Path(r"D:\temp\holographic_discovery_en.html")
PDF_OUT = BASE / "the-holographic-discovery-en.pdf"

EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

CSS = """
<style>
@page {
    size: A4;
    margin: 3.5cm 3cm 3.5cm 3.8cm;
    @top-left {
        content: '';
        font-size: 9pt;
        color: #666;
        font-style: italic;
    }
    @top-right {
        content: counter(page, lower-roman);
        font-size: 9pt;
        color: #666;
        font-style: italic;
        font-family: 'Georgia', serif;
    }
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        color: #555;
        font-family: 'Georgia', serif;
    }
}
@page :first {
    @top-left { content: ''; }
    @top-right { content: ''; }
    @bottom-center { content: ''; }
    margin: 0;
}
body {
    font-family: 'Georgia', 'Palatino Linotype', 'Book Antiqua', 'Times New Roman', serif;
    font-size: 12.5pt;
    line-height: 1.9;
    color: #1a1a1a;
    max-width: 100%;
    margin: 0;
    padding: 0;
    text-align: justify;
    hyphens: auto;
    orphans: 3;
    widows: 3;
}
.cover {
    page-break-after: always;
    height: 26cm;
    padding: 6cm 4cm 3cm 4cm;
    text-align: center;
    background: #f5f0eb;
    position: relative;
}
.cover:before {
    content: '';
    position: absolute;
    top: 1.5cm; left: 1.5cm; right: 1.5cm; bottom: 1.5cm;
    border: 1px solid #8b7a6a;
    pointer-events: none;
}
.cover h1 {
    font-family: 'Georgia', serif;
    font-size: 34pt;
    color: #2c1810;
    margin: 0 0 1.2cm 0;
    letter-spacing: 0.08em;
    font-weight: normal;
    line-height: 1.25;
    font-variant: small-caps;
}
.cover .subtitle {
    font-size: 11pt;
    color: #5a4a3a;
    font-style: italic;
    margin: 0 0 5cm 0;
    line-height: 1.6;
    letter-spacing: 0.03em;
}
.cover .author {
    font-size: 15pt;
    color: #2c1810;
    margin-top: 2cm;
    font-variant: small-caps;
    letter-spacing: 0.2em;
}
.cover .place {
    font-size: 10pt;
    color: #8a7a6a;
    margin-top: 0.5cm;
    font-style: italic;
}
.cover .footer {
    position: absolute;
    bottom: 2.5cm;
    left: 0; right: 0;
    text-align: center;
    font-size: 9pt;
    color: #8a7a6a;
    font-style: italic;
}
.toc {
    page-break-after: always;
    padding: 3cm 2cm;
}
.toc h1 {
    font-size: 18pt;
    color: #2c1810;
    border-bottom: 1px solid #8b7a6a;
    padding-bottom: 0.5cm;
    margin-bottom: 1cm;
    font-weight: normal;
    letter-spacing: 0.15em;
    font-variant: small-caps;
}
.toc ul { list-style: none; padding: 0; }
.toc li {
    padding: 0.2em 0;
    font-size: 10pt;
    letter-spacing: 0.03em;
}
.toc li.lv1 { padding-left: 0; margin-top: 0.3em; color: #2c1810; font-variant: small-caps; letter-spacing: 0.1em; }
.toc li.lv2 { padding-left: 1.2em; color: #5a4a3a; }
.toc a { color: inherit; text-decoration: none; border-bottom: 1px dotted #ccc; }

.doc { padding-top: 1cm; }
.doc h1.doc-title {
    display: none;
}
.doc div.doc-content {
    margin: 0;
    padding: 0;
}

.doc-content h1 {
    font-size: 20pt;
    color: #2c1810;
    font-weight: normal;
    text-align: center;
    font-variant: small-caps;
    letter-spacing: 0.12em;
    margin: 0 0 1.5cm 0;
    padding-bottom: 0.5cm;
    border-bottom: 1px solid #8b7a6a;
    page-break-before: always;
    padding-top: 1.5cm;
}
.doc-content h1:first-of-type {
    page-break-before: avoid;
    padding-top: 0;
}
.doc-content h2 {
    font-size: 16pt;
    color: #3a2a1a;
    font-weight: normal;
    font-style: italic;
    margin-top: 1.2cm;
    margin-bottom: 0.3cm;
    text-align: center;
    letter-spacing: 0.05em;
}
.doc-content h3 {
    font-size: 13pt;
    color: #5a4a3a;
    font-weight: normal;
    font-variant: small-caps;
    letter-spacing: 0.08em;
    margin-top: 0.8cm;
    margin-bottom: 0.3cm;
}
.doc-content p {
    margin: 0.3em 0;
    text-indent: 2em;
    line-height: 1.9;
    text-align: justify;
    word-spacing: 0.05em;
}
.doc-content p:first-of-type {
    text-indent: 0;
}
.doc-content p:first-of-type:first-letter {
    font-size: 3.2em;
    float: left;
    line-height: 0.85;
    margin-right: 0.12em;
    margin-top: 0.08em;
    color: #2c1810;
    font-family: 'Georgia', serif;
    font-weight: normal;
}
.doc-content ul, .doc-content ol {
    margin: 0.4em 0 0.4em 1.5em;
    padding-left: 1em;
}
.doc-content li {
    margin: 0.1em 0;
    line-height: 1.8;
}
.doc-content code {
    font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
    font-size: 9pt;
    background: #f5f0eb;
    padding: 0.08em 0.25em;
    color: #8b3a2a;
}
.doc-content pre {
    background: #f8f5f0;
    border: 1px solid #ddd;
    padding: 0.6em 0.8em;
    margin: 0.6em 0;
    font-size: 8.5pt;
    line-height: 1.4;
}
.doc-content pre code { background: transparent; padding: 0; color: #1a1a1a; }
.doc-content table {
    border-collapse: collapse;
    width: 90%;
    margin: 0.8em auto;
    font-size: 9.5pt;
}
.doc-content th, .doc-content td {
    border: 1px solid #bbb;
    padding: 0.25em 0.5em;
    text-align: left;
}
.doc-content th {
    background: #f0ebe5;
    font-weight: normal;
    font-variant: small-caps;
    letter-spacing: 0.05em;
}
.doc-content blockquote {
    border-left: 2px solid #8b7a6a;
    margin: 0.6em 0 0.6em 1.5em;
    padding: 0.2em 0 0.2em 1em;
    color: #5a4a3a;
    font-style: italic;
    font-size: 11pt;
    background: none;
}
.doc-content hr {
    border: none;
    text-align: center;
    margin: 1.5em 0;
}
.doc-content hr:after {
    content: '% % %';
    font-size: 10pt;
    color: #8b7a6a;
    letter-spacing: 0.5em;
}
.doc-content em {
    font-style: italic;
}
.doc-content strong {
    font-weight: normal;
    font-variant: small-caps;
    letter-spacing: 0.05em;
}
</style></style>
"""

def md_to_html(md_text):
    md = markdown.Markdown(extensions=["fenced_code", "tables", "codehilite"])
    return md.convert(md_text)

def collect_document(file_name):
    p = BASE / file_name
    if not p.exists():
        return f'<p style="color:red">File not found: {file_name}</p>'
    text = p.read_text(encoding="utf-8")
    return md_to_html(text)

def build_cover():
    return f"""
<div class="cover">
    <h1>The Holographic Discovery</h1>
    <div class="subtitle">
        A Treatise on the Unity of Living Form,<br>
        and the Mathematical Foundations of Inverse Inference<br>
        from the Surface to the Depth of the Organism
    </div>
    <div class="author">laimengjun</div>
    <div class="place">Xiamen, July 2026</div>
    <div class="footer">Written in the style of Edward Gibbon</div>
</div>
"""

def build_toc():
    return """
<div class="toc">
    <h1>Contents</h1>
    <ul>
        <li class="lv1"><a href="#doc-full">The Holographic Discovery</a></li>
    </ul>
</div>
"""

def build_book():
    cover = build_cover()
    toc = build_toc()
    html = collect_document("0.3-the-holographic-discovery-full.md")
    body = f'<div class="doc" id="doc-full"><h1 class="doc-title">The Holographic Discovery</h1><div class="doc-content">{html}</div></div>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>The Holographic Discovery</title>
    {CSS}
</head>
<body>
{cover}
{toc}
{body}
</body>
</html>"""

def main():
    print("=" * 60)
    print("English Monograph -> PDF Generator")
    print("=" * 60)
    
    print("\n[1/3] Building HTML ...")
    html = build_book()
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"  -> HTML: {HTML_OUT} ({len(html):,} chars)")
    
    print("\n[2/3] Edge headless print to PDF ...")
    t0 = time.time()
    cmd = [str(EDGE), "--headless=new", "--disable-gpu", "--no-sandbox",
           "--print-to-pdf=" + str(PDF_OUT), "--print-to-pdf-no-header",
           "file:///" + str(HTML_OUT).replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    print(f"  -> Time: {time.time() - t0:.1f}s")
    
    print("\n[3/3] Verifying ...")
    if PDF_OUT.exists():
        size_kb = PDF_OUT.stat().st_size / 1024
        print(f"  -> PDF: {PDF_OUT} ({size_kb:.1f} KB)")
    print("\nDone.")

if __name__ == "__main__":
    main()

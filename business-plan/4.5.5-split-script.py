# -*- coding: utf-8 -*-
"""
4.5.5-split-script.py - 把 30 集脚本拆分为:
  1) 4.5.2 video-prompts.md  (Seedance 2.5 视频生成 prompt + negative)
  2) 4.5.3 narration.md       (纯解说词, 用于 CosyVoice TTS)

设计:
  - 解析 4.5.1-30-ep-scripts.md 的标准结构 (Hook/上集/主体/AI 映射/金句/CTA)
  - 每个 segment 提取 视觉描述 (用于 Seedance) + 口播文字 (用于 TTS)
  - 视觉描述增强: 加入 cinematic 关键词, camera movement, lighting
  - 负面 prompt: 标准质量负面 (变形/低质/水印)
"""
import re
from pathlib import Path

INPUT = Path(r"D:\obsidian\Holographic-Biology\business-plan\4.5.1-30-ep-scripts.md")
VIDEO_OUT = Path(r"D:\obsidian\Holographic-Biology\business-plan\4.5.2-video-prompts.md")
NARRATION_OUT = Path(r"D:\obsidian\Holographic-Biology\business-plan\4.5.3-narration.md")

# 标准负面 prompt (适用于所有视觉片段)
STANDARD_NEGATIVE = (
    "low quality, blurry, deformed, ugly, watermark, text overlay, "
    "logo, signature, cropped, out of frame, worst quality, low resolution, "
    "bad anatomy, bad hands, missing fingers, extra fingers, "
    "duplicate, error, jpeg artifacts, morbid, gross proportions"
)

# 段类型视觉增强映射
VISUAL_ENHANCEMENT = {
    "Hook": "cinematic close-up, dramatic lighting, mysterious atmosphere, "
            "shallow depth of field, bold composition, vibrant colors",
    "上集回顾": "medium shot, documentary style, soft natural lighting, "
               "warm color palette, narrative pacing",
    "主体": "documentary style, clean composition, professional lighting, "
           "informative presentation, clear subject focus",
    "AI 映射": "futuristic aesthetic, cool blue tones, digital interface elements, "
              "modern tech atmosphere, dynamic motion",
    "金句": "cinematic wide shot, golden hour lighting, inspirational atmosphere, "
           "text overlay space, emotional resonance",
    "CTA": "warm inviting atmosphere, friendly tone, direct to camera feel, "
          "energetic pacing, call to action energy",
}

# 段类型时长 (秒)
SEGMENT_DURATION = {
    "Hook": 10,
    "上集回顾": 20,
    "主体": "60-90",
    "AI 映射": 60,
    "金句": 30,
    "CTA": 30,
}


def parse_episodes(md_text: str) -> list[dict]:
    """解析 4.5.1 markdown, 返回 30 集的结构化数据"""
    episodes = []
    # 切分每一集
    ep_pattern = re.compile(r"^## 第 (\d+) 集 · (.+?)$", re.MULTILINE)
    matches = list(ep_pattern.finditer(md_text))

    for i, m in enumerate(matches):
        ep_num = int(m.group(1))
        ep_title = m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        ep_body = md_text[start:end]

        episodes.append({
            "num": ep_num,
            "title": ep_title,
            "body": ep_body.strip(),
        })
    return episodes


def extract_segments(ep_body: str) -> list[dict]:
    """从一集内容提取标准段: Hook, 上集回顾, 主体, AI 映射, 金句, CTA"""
    segments = []
    # 段标题匹配
    seg_pattern = re.compile(
        r"\*\*【(Hook|上集回顾|主体|AI 映射|金句|CTA) · [^*]+?】\*\*\s*\n(.+?)(?=\n\*\*【|\n---|\Z)",
        re.DOTALL,
    )
    for m in seg_pattern.finditer(ep_body):
        seg_type = m.group(1)
        seg_content = m.group(2).strip()
        segments.append({"type": seg_type, "content": seg_content})
    return segments


def parse_body_subsections(seg_content: str) -> list[dict]:
    """从主体段提取小节 (一、二、三 等)"""
    subsections = []
    # 主体内的 **一、xxx** 等
    sub_pattern = re.compile(r"\*\*([一二三四五六七八九十]+)、(.+?)\*\*\s*\n(.+?)(?=\n\*\*[一二三四五六七八九十]+、|\Z)", re.DOTALL)
    for m in sub_pattern.finditer(seg_content):
        subsections.append({
            "num": m.group(1),
            "title": m.group(2),
            "content": m.group(3).strip(),
        })
    return subsections


def extract_visual_cues(text: str) -> str:
    """从段文字提取视觉描述关键词 (去重 + 清理)"""
    seen = set()
    cues = []

    def add_cue(cue):
        # 清理: 移除 "特写:" "动画:" 等前缀
        cue = re.sub(r"^(特写|动画|史料|地图|示意|画外音|背景|特写镜头|俯拍|仰拍)[：:]\s*", "", cue.strip())
        cue = cue.strip().strip("《》「」（）()[]").strip()
        if not cue or len(cue) < 4:
            return
        # 去重 (用简化后的文本作为 key)
        key = re.sub(r"[\s：:,。.、，：]+", "", cue)[:30]
        if key in seen:
            return
        seen.add(key)
        cues.append(cue)

    # 提取 (xxx) 括号内的视觉描述
    for m in re.finditer(r"[（(]([^）)]+)[）)]", text):
        inner = m.group(1)
        # 只取含镜头/视觉词的括号
        if any(kw in inner for kw in ["特写", "动画", "史料", "地图", "照片", "图", "镜头",
                                        "场景", "渲染", "示意", "对比", "扫描", "画", "底色", "建筑", "人物", "颜色", "实物", "动态", "缩放", "镜头", "图标", "表格", "数据", "裸照", "描边", "配文", "轮廓", "颜色", "动画", "锦上添花"]):
            add_cue(inner)

    return " ".join(cues)


def extract_narration_text(text: str) -> str:
    """从段文字提取纯口播内容 (移除视觉描述/元数据/视觉资产清单)"""
    # 移除 (xxx) 视觉括号
    text = re.sub(r"[（(][^）)]+[）)]", "", text)
    # 移除 **xxx** 加粗 (保留文字)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    # 移除 "动画:" "史料:" "特写:" "地图:" 等元数据标记行
    text = re.sub(r"^[A-Za-z\u4e00-\u9fff]+[：:][^\n]+\n", "", text, flags=re.MULTILINE)
    # 移除"视觉资产清单" 及其后内容
    text = re.sub(r"视觉资产清单[：:].*", "", text, flags=re.DOTALL)
    # 移除空标题 (如"一、xxx\n" 后无内容)
    text = re.sub(r"^([一二三四五六七八九十]+)、[^\n]*\n+(?=\n)", r"\1、", text, flags=re.MULTILINE)
    # 清理多余空白
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_video_prompt(seg_type: str, seg_content: str, ep_num: int, seg_idx: int) -> str:
    """为单个 segment 构造 Seedance 2.5 prompt"""
    visual = extract_visual_cues(seg_content)
    enhancement = VISUAL_ENHANCEMENT.get(seg_type, VISUAL_ENHANCEMENT["主体"])

    if visual:
        prompt = f"{visual}, {enhancement}"
    else:
        prompt = enhancement

    return prompt


def build_narration_for_segment(seg_type: str, seg_content: str) -> str:
    """提取 segment 的纯口播文字"""
    return extract_narration_text(seg_content)


# ============================================================
# 生成两个输出文件
# ============================================================
def generate_video_prompts_md(episodes: list[dict]) -> str:
    """生成 4.5.2 video-prompts.md"""
    out = []
    out.append("# 30 集视频生成 Prompts (Seedance 2.5)")
    out.append("")
    out.append("> **日期**: 2026-07-02")
    out.append("> **用途**: 驱动 Seedance 2.5 (字节跳动视频生成模型) 生成 30 集短视频")
    out.append("> **格式**: 每集包含多个 segment, 每个 segment 一个 prompt + 统一负面 prompt")
    out.append("")
    out.append("## 使用说明")
    out.append("")
    out.append("1. 每集时长约 8-12 分钟")
    out.append("2. 每集约 8-12 个 segment, 每个 segment 对应一个视频片段")
    out.append("3. **prompt** = 视觉描述 + 风格增强关键词")
    out.append("4. **negative_prompt** = 统一标准 (见末尾)")
    out.append("5. 建议 segment 时长:")
    out.append("   - Hook: 10s")
    out.append("   - 上集回顾: 20s")
    out.append("   - 主体小节: 60-90s")
    out.append("   - AI 映射: 60s")
    out.append("   - 金句: 30s")
    out.append("   - CTA: 30s")
    out.append("")
    out.append("---")
    out.append("")

    for ep in episodes:
        out.append(f"## 第 {ep['num']} 集 · {ep['title']}")
        out.append("")
        segments = extract_segments(ep["body"])

        seg_idx = 0
        for seg in segments:
            seg_idx += 1
            seg_type = seg["type"]
            seg_content = seg["content"]

            # 段时长
            duration = SEGMENT_DURATION.get(seg_type, 60)
            if isinstance(duration, str):
                duration_note = f"{duration} 秒"
            else:
                duration_note = f"{duration} 秒"

            # 主体段拆分小节
            if seg_type == "主体":
                subsections = parse_body_subsections(seg_content)
                if subsections:
                    for sub in subsections:
                        prompt = build_video_prompt(seg_type, sub["content"], ep["num"], seg_idx)
                        out.append(f"### Segment {seg_idx}.{sub['num']} {sub['title']} (主体 · ~70s)")
                        out.append("")
                        out.append(f"**prompt**:")
                        out.append("```")
                        out.append(prompt)
                        out.append("```")
                        out.append("")
                        out.append(f"**negative_prompt**: (见末尾统一负面)")
                        out.append("")
                    continue

            # 其他段
            prompt = build_video_prompt(seg_type, seg_content, ep["num"], seg_idx)
            out.append(f"### Segment {seg_idx} {seg_type} ({duration_note})")
            out.append("")
            out.append(f"**prompt**:")
            out.append("```")
            out.append(prompt)
            out.append("```")
            out.append("")
            out.append(f"**negative_prompt**: (见末尾统一负面)")
            out.append("")

        out.append("---")
        out.append("")

    # 统一负面 prompt
    out.append("## 统一负面 Prompt (适用于所有 segment)")
    out.append("")
    out.append("```")
    out.append(STANDARD_NEGATIVE)
    out.append("```")
    out.append("")
    out.append("---")
    out.append("")
    out.append(f"**总 segment 数**: 约 {sum(len(extract_segments(ep['body'])) for ep in episodes)} 个")
    out.append(f"**总时长**: 约 5 小时 (30 集 × 10 分钟)")
    out.append("")

    return "\n".join(out)


def generate_narration_md(episodes: list[dict]) -> str:
    """生成 4.5.3 narration.md (纯口播)"""
    out = []
    out.append("# 30 集短视频 解说词 (用于 TTS)")
    out.append("")
    out.append("> **日期**: 2026-07-02")
    out.append("> **用途**: CosyVoice TTS 合成 / 或其他语音合成工具")
    out.append("> **格式**: 纯口播文字, 移除所有视觉描述/动画提示/元数据")
    out.append("> **建议**: 整集一起合成 (比单句快 3-5x), 用同一声纹保持一致性")
    out.append("")
    out.append("## CosyVoice 调用示例")
    out.append("")
    out.append("```python")
    out.append("import sys, os")
    out.append("sys.path.insert(0, r'D:\\tools\\CosyVoice')")
    out.append("from cosyvoice.cli.cosyvoice import AutoModel")
    out.append("import torchaudio")
    out.append("")
    out.append("model = AutoModel(model_dir=r'D:\\models\\CosyVoice-300M')")
    out.append("prompt_wav = r'D:\\tools\\CosyVoice\\asset\\cross_lingual_prompt.wav'")
    out.append("prompt_text = '希望你以后能够做的比我还好呦。'")
    out.append("")
    out.append("for ep_num in range(1, 31):")
    out.append("    text = get_episode_text(ep_num)  # 读取本文件对应集")
    out.append("    for i, j in enumerate(model.inference_zero_shot(text, prompt_text, prompt_wav)):")
    out.append("        torchaudio.save(f'episode_{ep_num:02d}.wav', j['tts_speech'], model.sample_rate)")
    out.append("```")
    out.append("")
    out.append("---")
    out.append("")

    for ep in episodes:
        out.append(f"## 第 {ep['num']} 集 · {ep['title']}")
        out.append("")
        out.append("```")
        out.append(f"# 集 {ep['num']}: {ep['title']}")
        out.append("")

        segments = extract_segments(ep["body"])
        for seg in segments:
            seg_type = seg["type"]
            seg_content = seg["content"]
            narration = build_narration_for_segment(seg_type, seg_content)
            if narration:
                # 段标记 (TTS 可以用 [pause] 等控制标记)
                type_marker = {
                    "Hook": "[开场白]",
                    "上集回顾": "[上集回顾]",
                    "主体": "[主体内容]",
                    "AI 映射": "[AI 时代映射]",
                    "金句": "[金句]",
                    "CTA": "[结尾行动召唤]",
                }.get(seg_type, seg_type)
                out.append(f"# {type_marker}")
                out.append(narration)
                out.append("")

        out.append("```")
        out.append("")
        out.append("---")
        out.append("")

    out.append("## 统计")
    out.append("")
    out.append(f"- 总集数: {len(episodes)}")
    out.append(f"- 估计总字数: ~45,000 (每集 ~1,500)")
    out.append(f"- 估计总音频时长: ~5 小时 (每集 10 分钟)")
    out.append(f"- 估计处理时间: ~30-60 分钟 (CosyVoice 推理)")
    out.append("")
    out.append("## 声音一致性建议")
    out.append("")
    out.append("- 30 集用**同一段** `prompt_wav` (cross_lingual_prompt.wav)")
    out.append("- 同一段 `prompt_text` (希望你以后能够做的比我还好呦。)")
    out.append("- 如需个性化声音, 录制 10 秒干净的参考音频替换 prompt_wav")
    out.append("- 模型加载 ~40s, 一次会话内可复用, 不要每集重新加载")
    out.append("")

    return "\n".join(out)


def main():
    print("=" * 60)
    print("4.5.1 → 4.5.2 + 4.5.3 拆分脚本")
    print("=" * 60)

    # 读原文件
    md_text = INPUT.read_text(encoding="utf-8")
    print(f"读入: {INPUT} ({len(md_text):,} chars)")

    # 解析
    episodes = parse_episodes(md_text)
    print(f"解析: {len(episodes)} 集")

    # 生成 video prompts
    print("\n[1/2] 生成 4.5.2 video-prompts.md ...")
    video_md = generate_video_prompts_md(episodes)
    VIDEO_OUT.write_text(video_md, encoding="utf-8")
    print(f"  → {VIDEO_OUT} ({len(video_md):,} chars)")

    # 生成 narration
    print("\n[2/2] 生成 4.5.3 narration.md ...")
    narr_md = generate_narration_md(episodes)
    NARRATION_OUT.write_text(narr_md, encoding="utf-8")
    print(f"  → {NARRATION_OUT} ({len(narr_md):,} chars)")

    print("\n完成。")


if __name__ == "__main__":
    main()
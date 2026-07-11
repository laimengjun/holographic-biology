# -*- coding: utf-8 -*-
"""
4.5.6-cosyvoice-batch.py - 用 CosyVoice 批量生成 30 集语音

设计:
  - 读取 4.5.3 narration.md, 提取每集纯口播文字
  - 模型只加载一次 (避免每集 38s 加载)
  - 每集一个 wav 文件: episode_01.wav ~ episode_30.wav
  - 输出目录: D:\obsidian\Holographic-Biology\business-plan\voice\

用法:
  python 4.5.6-cosyvoice-batch.py              # 生成全部 30 集
  python 4.5.6-cosyvoice-batch.py --ep 1       # 只生成第 1 集 (测试)
  python 4.5.6-cosyvoice-batch.py --ep 1-5     # 生成 1-5 集
"""
import argparse
import os
import re
import sys
import time
from pathlib import Path

# CosyVoice 路径
COSYVOICE_DIR = r'D:\tools\CosyVoice'
MODEL_DIR = r'D:\models\CosyVoice-300M'

# 路径设置
sys.path.insert(0, COSYVOICE_DIR)
sys.path.insert(0, os.path.join(COSYVOICE_DIR, 'third_party', 'Matcha-TTS'))

NARRATION_FILE = Path(r'D:\obsidian\Holographic-Biology\business-plan\4.5.3-narration.md')
VOICE_DIR = Path(r'D:\obsidian\Holographic-Biology\business-plan\voice')
PROMPT_WAV = os.path.join(COSYVOICE_DIR, 'asset', 'cross_lingual_prompt.wav')
PROMPT_TEXT = "希望你以后能够做的比我还好呦。"


def parse_episode_text(md_text: str, ep_num: int) -> str:
    """从 narration.md 提取指定集的口播文字 (清理 markdown 标记)"""
    # 找到 "## 第 N 集" 段
    pattern = rf"## 第 {ep_num} 集 · (.+?)\n\n```\n(.+?)```"
    m = re.search(pattern, md_text, re.DOTALL)
    if not m:
        return ""
    title = m.group(1)
    body = m.group(2)

    # 移除 markdown 标记
    body = re.sub(r"^#.*$", "", body, flags=re.MULTILINE)  # 标题行
    body = re.sub(r"^\s*$", "", body, flags=re.MULTILINE)  # 空行
    # 把 # [开场白] 转换为 [pause] 等 TTS 标记
    body = re.sub(r"#\s*\[(开场白|上集回顾|主体内容|AI 时代映射|金句|结尾行动召唤)\]",
                  lambda m: f"\n\n[{m.group(1)}]\n", body)

    return f"全息生物学三十集课程，{title}。\n\n{body.strip()}"


def split_long_text(text: str, max_chars: int = 200) -> list[str]:
    """把长文本拆成不超过 max_chars 的小段 (在句号/逗号处断)"""
    if len(text) <= max_chars:
        return [text]

    parts = []
    current = ""
    for char in text:
        current += char
        if char in "。！？\n" and len(current) >= max_chars * 0.5:
            parts.append(current)
            current = ""
        elif len(current) >= max_chars:
            # 强制切分 (在最近的逗号处)
            idx = current.rfind("，")
            if idx > 0:
                parts.append(current[:idx + 1])
                current = current[idx + 1:]
            else:
                parts.append(current)
                current = ""
    if current:
        parts.append(current)
    return parts


def synthesize_episode(model, ep_num: int, text: str, sample_rate: int) -> str:
    """合成单集音频, 返回输出文件路径"""
    output_path = VOICE_DIR / f"episode_{ep_num:02d}.wav"

    # 拆分长文本 (CosyVoice 一次推理有限制)
    parts = split_long_text(text, max_chars=300)
    print(f"  [集 {ep_num}] 文本 {len(text)} 字符, 拆为 {len(parts)} 段")

    # 合成所有段
    all_speech = []
    for i, part in enumerate(parts, 1):
        if not part.strip():
            continue
        print(f"    段 {i}/{len(parts)}: {part[:30]}...")
        for j, output in enumerate(model.inference_zero_shot(part, PROMPT_TEXT, PROMPT_WAV)):
            all_speech.append(output['tts_speech'])

    # 拼接所有段
    if not all_speech:
        print(f"  [集 {ep_num}] 警告: 无音频生成")
        return ""

    import torch
    combined = torch.cat(all_speech, dim=1)

    # 保存
    import torchaudio
    torchaudio.save(str(output_path), combined, sample_rate)
    print(f"  [集 {ep_num}] → {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description="CosyVoice 批量生成 30 集语音")
    parser.add_argument("--ep", type=str, default="1-30", help="集数范围, 如 '1-5' 或 '3'")
    parser.add_argument("--dry-run", action="store_true", help="只显示文本, 不合成")
    args = parser.parse_args()

    # 解析集数范围
    if "-" in args.ep:
        start, end = map(int, args.ep.split("-"))
        episodes = list(range(start, end + 1))
    else:
        ep = int(args.ep)
        episodes = [ep]

    # 读 narration
    md_text = NARRATION_FILE.read_text(encoding="utf-8")
    print(f"读入: {NARRATION_FILE} ({len(md_text):,} chars)")

    # 确保输出目录存在
    VOICE_DIR.mkdir(parents=True, exist_ok=True)

    # dry-run 模式: 只打印
    if args.dry_run:
        for ep in episodes:
            text = parse_episode_text(md_text, ep)
            print(f"\n=== 集 {ep} ({len(text)} 字符) ===")
            print(text[:500])
            print("...")
        return

    # 加载模型
    print(f"\n[1/2] 加载 CosyVoice 模型 ({MODEL_DIR})...")
    t0 = time.time()
    import torchaudio
    import torch
    from cosyvoice.cli.cosyvoice import AutoModel
    model = AutoModel(model_dir=MODEL_DIR)
    sample_rate = model.sample_rate
    print(f"  模型加载: {time.time() - t0:.1f}s, sample_rate={sample_rate}Hz")

    # 批量生成
    print(f"\n[2/2] 合成 {len(episodes)} 集语音...")
    t_start = time.time()
    results = []
    for ep in episodes:
        text = parse_episode_text(md_text, ep)
        if not text:
            print(f"  [集 {ep}] 错误: 未找到口播文字")
            continue
        t0 = time.time()
        path = synthesize_episode(model, ep, text, sample_rate)
        results.append((ep, path, time.time() - t0))

    # 总结
    total_time = time.time() - t_start
    print(f"\n=== 完成 ===")
    print(f"总用时: {total_time:.1f}s")
    print(f"输出目录: {VOICE_DIR}")
    print(f"成功: {len([r for r in results if r[1]])}/{len(episodes)} 集")
    for ep, path, sec in results:
        if path:
            print(f"  集 {ep}: {sec:.1f}s -> {path}")


if __name__ == "__main__":
    main()
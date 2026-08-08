#!/usr/bin/env python3
"""阶段5：TTS配音 + SRT字幕生成。

- edge-tts 生成每句旁白 MP3
- mutagen 读取 MP3 时长（不用 ffprobe，精简版不支持 MP3 解码）
- 按音频实际时长累加生成 SRT
- 合并每段音频为单个 wav（ffmpeg concat）
"""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
from mutagen.mp3 import MP3

FFMPEG = r"C:\ffmpeg\ffmpeg-6.1.1-essentials_build\bin\ffmpeg.exe"
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "+0%"
GAP_BETWEEN_LINES = 0.15  # 句间间隔150ms

BASE_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6")
NARRATION_FILE = BASE_DIR / "narration.json"
AUDIO_DIR = BASE_DIR / "audio"
SRT_DIR = BASE_DIR / "srt"
SRT_DIR.mkdir(parents=True, exist_ok=True)


def fmt_srt_time(seconds: float) -> str:
    """秒 -> SRT时间格式 HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


async def gen_tts(text: str, out_mp3: Path) -> float:
    """生成单句TTS并返回时长（秒）。"""
    comm = edge_tts.Communicate(text, VOICE, rate=RATE)
    await comm.save(out_mp3)
    await asyncio.sleep(0.15)  # 等待文件写入完成
    audio = MP3(str(out_mp3))
    return audio.info.length


async def gen_segment_audio(seg: dict, seg_idx: int, global_time: float) -> tuple[list[dict], float]:
    """生成一个segment的所有旁白音频 + SRT条目。"""
    seg_name = seg["name"]
    seg_audio_dir = AUDIO_DIR / f"segment_{seg_idx:02d}_{seg_name}"
    seg_audio_dir.mkdir(parents=True, exist_ok=True)

    srt_entries = []
    mp3_files = []
    cur_t = global_time

    for i, line in enumerate(seg["lines"]):
        mp3_path = seg_audio_dir / f"line_{i:03d}.mp3"
        dur = await gen_tts(line["text"], mp3_path)
        srt_entries.append({
            "idx": len(srt_entries) + 1,
            "start": cur_t,
            "end": cur_t + dur,
            "text": line["text"],
        })
        mp3_files.append(mp3_path)
        cur_t += dur + GAP_BETWEEN_LINES
        print(f"  [{seg_name}] line{i:03d} ({dur:.2f}s) {line['text'][:30]}...")

    # 合并MP3为单个WAV
    seg_wav = AUDIO_DIR / f"segment_{seg_idx:02d}_{seg_name}.wav"
    concat_file = seg_audio_dir / "concat.txt"
    concat_content = "\n".join(f"file '{mp3}'" for mp3 in mp3_files)
    concat_file.write_text(concat_content, encoding="utf-8")

    cmd = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-vn", "-acodec", "pcm_s16le", "-ar", "48000", "-ac", "1",
        str(seg_wav)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f"  [WARN] 合并音频失败: {r.stderr[:200]}")

    seg_dur = cur_t - global_time
    print(f"  [{seg_name}] 合并完成: {seg_wav.name} ({seg_dur:.2f}s)")
    return srt_entries, seg_dur


async def main_async() -> int:
    narration = json.loads(NARRATION_FILE.read_text(encoding="utf-8"))
    all_srt = []
    global_time = 0.5  # 片头0.5s开始

    print("=== 阶段5：TTS配音生成 ===")
    for seg_idx, seg in enumerate(narration["segments"]):
        print(f"\n--- {seg['name']} ---")
        srt_entries, seg_dur = await gen_segment_audio(seg, seg_idx, global_time)
        all_srt.extend(srt_entries)
        global_time += seg_dur

    # 写SRT文件
    srt_path = SRT_DIR / "compilation.srt"
    lines = []
    for i, entry in enumerate(all_srt, 1):
        lines.append(str(i))
        lines.append(f"{fmt_srt_time(entry['start'])} --> {fmt_srt_time(entry['end'])}")
        lines.append(entry["text"])
        lines.append("")
    srt_path.write_text("\n".join(lines), encoding="utf-8")

    total_dur = global_time
    print(f"\n=== 完成 ===")
    print(f"  字幕: {len(all_srt)} 条 -> {srt_path}")
    print(f"  总时长: {total_dur:.1f}s ({int(total_dur//60)}分{int(total_dur%60)}秒)")
    return 0


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())

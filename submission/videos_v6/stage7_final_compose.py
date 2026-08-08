#!/usr/bin/env python3
"""阶段7：拼接所有segment + 字幕烧录 → 最终视频。

流程：
1. concat demuxer拼接7个segment（copy编码，快）
2. 烧录完整字幕到拼接后的视频（重新编码，慢）
3. 输出最终 narration_full.mp4

关键踩坑：
- 字幕路径Windows转义：\\ → / 和 : → \\:
- 所有segment已有音频流，concat不会丢音频
"""
from __future__ import annotations

import subprocess
from pathlib import Path

FFMPEG = r"C:\ffmpeg\ffmpeg-6.1.1-essentials_build\bin\ffmpeg.exe"
FPS = 30

BASE_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6")
SEGMENTS_DIR = BASE_DIR / "segments"
SRT_FILE = BASE_DIR / "srt" / "compilation.srt"
FINAL_DIR = BASE_DIR / "final"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

# 按顺序拼接的segment文件
SEGMENT_FILES = [
    "seg_00_intro.mp4",
    "seg_01_L1.mp4",
    "seg_02_L2.mp4",
    "seg_03_L3.mp4",
    "seg_04_L4.mp4",
    "seg_05_L5.mp4",
    "seg_06_outro.mp4",
]


def concat_segments(out_path: Path) -> bool:
    """用concat demuxer拼接所有segment（copy编码，无质量损失）。"""
    concat_file = BASE_DIR / "concat_list.txt"
    lines = []
    for fname in SEGMENT_FILES:
        seg_path = SEGMENTS_DIR / fname
        if not seg_path.exists():
            print(f"  [ERROR] 缺失: {fname}")
            return False
        # Windows路径用正斜杠
        lines.append(f"file '{seg_path.as_posix()}'")
    concat_file.write_text("\n".join(lines), encoding="utf-8")

    cmd = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        "-movflags", "+faststart",
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    concat_file.unlink(missing_ok=True)
    if r.returncode != 0:
        print(f"  [FAIL] concat: {r.stderr[-400:]}")
    return r.returncode == 0


def burn_subtitles(video_path: Path, srt_path: Path, out_path: Path) -> bool:
    """烧录字幕到视频。"""
    # Windows路径转义：\\ → / 和 : → \\:
    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")
    vf = (
        f"subtitles='{srt_escaped}':"
        f"force_style='FontName=Microsoft YaHei,"
        f"FontSize=22,PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,"
        f"BorderStyle=1,Outline=3,Alignment=2,MarginV=60'"
    )

    cmd = [
        FFMPEG, "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "copy",  # 音频直接复制，不重新编码
        "-movflags", "+faststart",
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  [FAIL] burn_subtitles: {r.stderr[-400:]}")
    return r.returncode == 0


def main() -> int:
    print("=== 阶段7：最终拼接 + 字幕烧录 ===")

    # 1. 拼接所有segment
    concat_out = FINAL_DIR / "concat_no_subtitle.mp4"
    print(f"\n[1/2] 拼接 {len(SEGMENT_FILES)} 个segment...")
    if not concat_segments(concat_out):
        return 1
    size_mb = concat_out.stat().st_size / (1024 * 1024)
    print(f"  => {concat_out.name} ({size_mb:.1f}MB)")

    # 2. 烧录字幕
    final_out = FINAL_DIR / "narration_full.mp4"
    print(f"\n[2/2] 烧录字幕 -> {final_out.name}...")
    if not burn_subtitles(concat_out, SRT_FILE, final_out):
        return 1

    final_mb = final_out.stat().st_size / (1024 * 1024)
    print(f"\n=== 最终视频: {final_out} ({final_mb:.1f}MB) ===")

    # 清理中间文件
    concat_out.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

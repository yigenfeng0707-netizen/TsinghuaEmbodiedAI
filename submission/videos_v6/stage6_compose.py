#!/usr/bin/env python3
"""阶段6：ffmpeg Ken Burns合成每关视频 + 音频合并。

- 为每句旁白的照片生成Ken Burns视频片段（时长=TTS时长）
- 拼接每个segment的所有片段为segment视频
- 合并音频到segment视频
- 字幕在阶段7最终拼接时统一烧录
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

FFMPEG = r"C:\ffmpeg\ffmpeg-6.1.1-essentials_build\bin\ffmpeg.exe"
FPS = 30
TARGET_W, TARGET_H = 1920, 1080

BASE_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6")
NARRATION_FILE = BASE_DIR / "narration.json"
SRT_FILE = BASE_DIR / "srt" / "compilation.srt"
AUDIO_DIR = BASE_DIR / "audio"
SEGMENTS_DIR = BASE_DIR / "segments"
SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)


def parse_srt(srt_path: Path) -> list[dict]:
    """解析SRT文件，返回[{idx, start, end, text}]。"""
    content = srt_path.read_text(encoding="utf-8").strip()
    blocks = re.split(r"\n\s*\n", content)
    entries = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        idx = int(lines[0])
        time_match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", lines[1])
        if not time_match:
            continue
        start = srt_time_to_seconds(time_match.group(1))
        end = srt_time_to_seconds(time_match.group(2))
        text = "\n".join(lines[2:])
        entries.append({"idx": idx, "start": start, "end": end, "text": text})
    return entries


def srt_time_to_seconds(t: str) -> float:
    """SRT时间 -> 秒"""
    h, m, s_ms = t.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def gen_kenburns_filter(zoom_type: str, duration: float) -> str:
    """生成zoompan滤镜字符串。

    关键修复：
    - scale 从 8000 降到 3840，使用 lanczos 插值避免像素化
    - left/right 的 x 坐标公式修正：x 范围必须在 [0, iw-iw/z] 内，
      否则窗口超出图片边界，产生黑色填充伪影（"乱码"现象的根因）
    - in/out 的 x/y 居中公式修正为动态跟随 z 值
    """
    frames = max(1, int(duration * FPS))
    # 输入 1920x1080 → scale 到 3840x2160（2倍，lanczos 插值）
    scale_prefix = f"scale=3840:-1:flags=lanczos,"
    if zoom_type == "in":
        # 缓慢放大：z 1.0→1.15，x/y 居中跟随
        return (f"{scale_prefix}zoompan=z='min(zoom+0.0008,1.15)':"
                f"x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':"
                f"d={frames}:s={TARGET_W}x{TARGET_H}:fps={FPS}")
    elif zoom_type == "out":
        # 缓慢缩小：z 1.15→1.0，x/y 居中跟随
        return (f"{scale_prefix}zoompan=z='1.15-0.0008*on':"
                f"x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':"
                f"d={frames}:s={TARGET_W}x{TARGET_H}:fps={FPS}")
    elif zoom_type == "left":
        # 向左平移：z=1.1，x 从最大值→0（x_max = iw-iw/z ≈ 349）
        return (f"{scale_prefix}zoompan=z=1.1:"
                f"x='(iw-iw/zoom)*(1-on/{frames})':y='ih/2-(ih/zoom)/2':"
                f"d={frames}:s={TARGET_W}x{TARGET_H}:fps={FPS}")
    elif zoom_type == "right":
        # 向右平移：z=1.1，x 从 0→最大值
        return (f"{scale_prefix}zoompan=z=1.1:"
                f"x='(iw-iw/zoom)*on/{frames}':y='ih/2-(ih/zoom)/2':"
                f"d={frames}:s={TARGET_W}x{TARGET_H}:fps={FPS}")
    else:  # static
        return (f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=decrease,"
                f"pad={TARGET_W}:{TARGET_H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS}")


def gen_kenburns_clip(img_path: str, out_path: Path, duration: float, zoom_type: str) -> bool:
    """生成Ken Burns视频片段。"""
    vf = gen_kenburns_filter(zoom_type, duration)
    cmd = [
        FFMPEG, "-y", "-loop", "1", "-i", img_path,
        "-vf", vf, "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"    [FAIL] {out_path.name}: {r.stderr[-300:]}")
    return r.returncode == 0


def concat_clips(clip_paths: list[Path], out_path: Path) -> bool:
    """用concat demuxer拼接视频片段。"""
    concat_file = out_path.parent / f"{out_path.stem}_concat.txt"
    concat_content = "\n".join(f"file '{p}'" for p in clip_paths)
    concat_file.write_text(concat_content, encoding="utf-8")

    cmd = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    concat_file.unlink(missing_ok=True)
    return r.returncode == 0


def merge_audio_video(video_path: Path, audio_path: Path, out_path: Path) -> bool:
    """合并音频和视频，用tpad延长视频跟随音频时长。"""
    cmd = [
        FFMPEG, "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "1",
        "-shortest",
        "-movflags", "+faststart",
        str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"    [FAIL] merge: {r.stderr[-300:]}")
    return r.returncode == 0


def main() -> int:
    narration = json.loads(NARRATION_FILE.read_text(encoding="utf-8"))
    srt_entries = parse_srt(SRT_FILE)
    print(f"=== 阶段6：Ken Burns视频合成（{len(srt_entries)}句旁白）===")

    line_idx = 0
    for seg_idx, seg in enumerate(narration["segments"]):
        seg_name = seg["name"]
        print(f"\n--- {seg_name} ({len(seg['lines'])}句) ---")

        seg_clips_dir = SEGMENTS_DIR / f"seg_{seg_idx:02d}_{seg_name}_clips"
        seg_clips_dir.mkdir(parents=True, exist_ok=True)

        clip_paths = []
        for i, line in enumerate(seg["lines"]):
            entry = srt_entries[line_idx]
            duration = entry["end"] - entry["start"]
            clip_path = seg_clips_dir / f"clip_{i:03d}.mp4"
            ok = gen_kenburns_clip(line["photo"], clip_path, duration, line["zoom"])
            if ok:
                clip_paths.append(clip_path)
                print(f"  clip{i:03d} ({duration:.2f}s, {line['zoom']:6s}) OK")
            line_idx += 1

        # 拼接片段
        seg_video_no_audio = SEGMENTS_DIR / f"seg_{seg_idx:02d}_{seg_name}_video.mp4"
        if not concat_clips(clip_paths, seg_video_no_audio):
            print(f"  [FAIL] 拼接失败: {seg_name}")
            continue

        # 合并音频
        seg_audio = AUDIO_DIR / f"segment_{seg_idx:02d}_{seg_name}.wav"
        seg_final = SEGMENTS_DIR / f"seg_{seg_idx:02d}_{seg_name}.mp4"
        if merge_audio_video(seg_video_no_audio, seg_audio, seg_final):
            size_mb = seg_final.stat().st_size / (1024 * 1024)
            print(f"  => {seg_final.name} ({size_mb:.1f}MB) OK")
        else:
            print(f"  [FAIL] 合并音频失败: {seg_name}")

    print(f"\n=== 完成 -> {SEGMENTS_DIR} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

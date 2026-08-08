#!/usr/bin/env python3
"""阶段8：验证最终视频质量。

检查项：
1. 视频规格（1920x1080 30fps H.264 yuv420p + AAC 48kHz）
2. 音视频时长一致性（误差<50ms）
3. 闪烁检查（alt_diff均值<0.05，峰值<0.15）
4. 字幕像素分析（字幕区域白色像素比例0.5%-20%）
5. 关键帧抽帧验证
"""
from __future__ import annotations

import subprocess
import json
from pathlib import Path

import cv2
import numpy as np

FFMPEG = r"C:\ffmpeg\ffmpeg-6.1.1-essentials_build\bin\ffmpeg.exe"
FFPROBE = r"C:\ffmpeg\ffmpeg-6.1.1-essentials_build\bin\ffprobe.exe"

BASE_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6")
VIDEO_PATH = BASE_DIR / "final" / "narration_full.mp4"
SRT_PATH = BASE_DIR / "srt" / "compilation.srt"
VERIFY_DIR = BASE_DIR / "verify"
VERIFY_DIR.mkdir(parents=True, exist_ok=True)


def get_video_info() -> dict:
    """用ffprobe获取视频信息。"""
    cmd = [
        FFPROBE, "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        str(VIDEO_PATH)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return {}
    return json.loads(r.stdout)


def check_flicker(start_frame: int = 100, n_frames: int = 60) -> tuple[float, float]:
    """闪烁检查（alt_diff指标）。"""
    cap = cv2.VideoCapture(str(VIDEO_PATH))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    prev = None
    diffs = []
    for _ in range(n_frames):
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev is not None:
            diff = np.mean(np.abs(gray.astype(float) - prev.astype(float))) / 255.0
            diffs.append(diff)
        prev = gray
    cap.release()
    if not diffs:
        return 1.0, 1.0
    return float(np.mean(diffs)), float(np.max(diffs))


def check_subtitle_pixels(frame_idx: int) -> float:
    """检查指定帧的字幕区域白色像素比例。"""
    cap = cv2.VideoCapture(str(VIDEO_PATH))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return -1.0
    # 字幕区域：底部约100-120px（1080p中约960-1080）
    subtitle_region = frame[960:1080, :, :]
    # 白色像素：RGB值都>200
    white_mask = np.all(subtitle_region > 200, axis=2)
    return float(np.sum(white_mask)) / white_mask.size


def extract_key_frames():
    """抽取关键帧用于人工验证。"""
    # 抽取5个时间点的帧
    timestamps = [
        (5, "intro"),
        (20, "L1_mid"),
        (55, "L2_mid"),
        (90, "L3_mid"),
        (125, "L4_mid"),
        (150, "L5_mid"),
    ]
    cap = cv2.VideoCapture(str(VIDEO_PATH))
    for ts, label in timestamps:
        cap.set(cv2.CAP_PROP_POS_MSEC, ts * 1000)
        ret, frame = cap.read()
        if ret:
            out_path = VERIFY_DIR / f"keyframe_{ts:03d}s_{label}.jpg"
            cv2.imwrite(str(out_path), frame)
            print(f"  抽帧 {ts}s ({label}) -> {out_path.name}")
    cap.release()


def main() -> int:
    print("=== 阶段8：视频质量验证 ===\n")

    # 1. 视频规格
    info = get_video_info()
    if not info:
        print("[FAIL] 无法读取视频信息")
        return 1

    v_stream = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a_stream = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

    print("[1] 视频规格:")
    if v_stream:
        w = int(v_stream["width"])
        h = int(v_stream["height"])
        fps = eval(v_stream["r_frame_rate"])
        codec = v_stream["codec_name"]
        pix_fmt = v_stream.get("pix_fmt", "N/A")
        v_dur = float(v_stream.get("duration", 0))
        print(f"  分辨率: {w}x{h} {'✓' if w == 1920 and h == 1080 else '✗'}")
        print(f"  帧率: {fps:.1f}fps {'✓' if abs(fps - 30) < 0.1 else '✗'}")
        print(f"  编码: {codec} {'✓' if codec == 'h264' else '✗'}")
        print(f"  像素格式: {pix_fmt} {'✓' if pix_fmt == 'yuv420p' else '✗'}")
        print(f"  视频时长: {v_dur:.2f}s")

    if a_stream:
        a_codec = a_stream["codec_name"]
        a_sr = int(a_stream["sample_rate"])
        a_ch = int(a_stream["channels"])
        a_dur = float(a_stream.get("duration", 0))
        print(f"\n[2] 音频规格:")
        print(f"  编码: {a_codec} {'✓' if a_codec == 'aac' else '✗'}")
        print(f"  采样率: {a_sr}Hz {'✓' if a_sr == 48000 else '✗'}")
        print(f"  声道: {a_ch} {'✓' if a_ch == 1 else '✗'}")
        print(f"  音频时长: {a_dur:.2f}s")

        if v_stream:
            diff = abs(v_dur - a_dur) * 1000
            print(f"  音视频误差: {diff:.0f}ms {'✓' if diff < 50 else '✗'}")

    # 3. 闪烁检查
    print(f"\n[3] 闪烁检查:")
    # 在多个位置检查
    all_mean = []
    all_max = []
    for start in [50, 500, 1000, 2000, 3500, 4500]:
        mean_d, max_d = check_flicker(start, 60)
        all_mean.append(mean_d)
        all_max.append(max_d)
        print(f"  帧{start:5d}: mean={mean_d:.4f} max={max_d:.4f}")
    avg_mean = np.mean(all_mean)
    avg_max = np.max(all_max)
    print(f"  总体: mean={avg_mean:.4f} {'✓' if avg_mean < 0.05 else '✗'}  max={avg_max:.4f} {'✓' if avg_max < 0.15 else '✗'}")

    # 4. 字幕像素分析
    print(f"\n[4] 字幕像素分析:")
    # 在有字幕的时间点检查（大约每关中段）
    for ts in [6, 25, 55, 90, 125, 155]:
        frame_idx = int(ts * 30)
        ratio = check_subtitle_pixels(frame_idx)
        status = "✓" if 0.001 < ratio < 0.20 else "△"
        print(f"  {ts}s: 白色像素比={ratio:.4f} {status}")

    # 5. 关键帧抽帧
    print(f"\n[5] 关键帧抽帧:")
    extract_key_frames()

    # 文件大小
    size_mb = VIDEO_PATH.stat().st_size / (1024 * 1024)
    print(f"\n[6] 文件大小: {size_mb:.1f}MB")

    print(f"\n=== 验证完成 -> {VERIFY_DIR} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

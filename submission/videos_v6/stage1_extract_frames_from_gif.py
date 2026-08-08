#!/usr/bin/env python3
"""阶段1：从回放GIF抽帧作为照片素材（替代docx提取方案）。

每个GIF均匀抽取关键帧，按关卡和视角分类保存。
- grasp GIF：抽3帧（抓取前/中/后）
- replay GIF：抽4帧（起始/导航/抓取/放置）
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image

GIF_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\JCIIOT\submission\replay_gifs")
OUT_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6\photos")

# 每类GIF抽帧数量
FRAMES_PER_GRASP = 3
FRAMES_PER_REPLAY = 4

# GIF文件清单：[(文件名, 视角标签, 帧数)]
GIF_LIST = [
    # L1（仅2个GIF，无robot0_robotview回放）
    ("L1_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L1_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    # L2
    ("L2_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L2_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    ("L2_replay_robot0_robotview.gif", "robotview",FRAMES_PER_REPLAY),
    # L3
    ("L3_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L3_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    ("L3_replay_robot0_robotview.gif", "robotview",FRAMES_PER_REPLAY),
    # L4
    ("L4_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L4_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    ("L4_replay_robot0_robotview.gif", "robotview",FRAMES_PER_REPLAY),
    # L5
    ("L5_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L5_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    ("L5_replay_robot0_robotview.gif", "robotview",FRAMES_PER_REPLAY),
]


def extract_gif_frames(gif_path: Path, n_frames: int, out_prefix: Path) -> list[Path]:
    """从GIF均匀抽取n_frames帧，保存为PNG。"""
    img = Image.open(gif_path)
    total = img.n_frames
    if total <= n_frames:
        indices = list(range(total))
    else:
        # 均匀分布，跳过开头几帧（通常是初始状态）和末尾暂停帧
        start = max(1, total // 10)
        end = min(total - 2, total * 9 // 10)  # 跳过末尾暂停帧
        step = max(1, (end - start) // (n_frames - 1))
        indices = [min(start + i * step, end) for i in range(n_frames)]

    saved = []
    for i, idx in enumerate(indices):
        img.seek(idx)
        frame = img.convert("RGB")
        out_path = Path(f"{out_prefix}_{i+1:02d}.png")
        frame.save(out_path, "PNG")
        saved.append(out_path)
        print(f"  [{idx:4d}/{total}] -> {out_path.name} ({frame.size[0]}x{frame.size[1]})")
    return saved


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0

    for gif_name, view, n_frames in GIF_LIST:
        gif_path = GIF_DIR / gif_name
        if not gif_path.exists():
            print(f"[SKIP] {gif_name} 不存在")
            continue

        level = gif_name.split("_")[0]  # L1 / L2 ...
        level_dir = OUT_DIR / level
        level_dir.mkdir(parents=True, exist_ok=True)

        prefix = level_dir / f"{level}_{view}"
        print(f"\n=== {gif_name} -> {n_frames}帧 ===")
        saved = extract_gif_frames(gif_path, n_frames, prefix)
        total += len(saved)

    print(f"\n=== 完成：共抽取 {total} 张照片 -> {OUT_DIR} ===")

    # 统计每关帧数
    for level in ["L1", "L2", "L3", "L4", "L5"]:
        ld = OUT_DIR / level
        if ld.exists():
            n = len(list(ld.glob("*.png")))
            print(f"  {level}: {n} 张")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

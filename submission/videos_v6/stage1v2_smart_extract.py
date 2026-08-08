#!/usr/bin/env python3
"""阶段1v2：智能抽帧 — 从GIF中选择质量最好的帧（跳过渲染异常帧）。

异常帧判定：8x8块方差<5的比例>0.20（像素化/渲染失败）。
对每个GIF，扫描所有帧的质量，只选择正常帧中均匀分布的N帧。
如果某个GIF所有帧都异常（如L4_grasp），标记为需替代。
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image
import numpy as np

GIF_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\JCIIOT\submission\replay_gifs")
OUT_DIR = Path(r"d:\APPs\TsinghuaEmbodiedAI\submission\videos_v6\photos")

FRAMES_PER_GRASP = 3
FRAMES_PER_REPLAY = 4

GIF_LIST = [
    ("L1_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L1_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    ("L2_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L2_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    ("L2_replay_robot0_robotview.gif", "robotview",FRAMES_PER_REPLAY),
    ("L3_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L3_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    ("L3_replay_robot0_robotview.gif", "robotview",FRAMES_PER_REPLAY),
    ("L4_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L4_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    ("L4_replay_robot0_robotview.gif", "robotview",FRAMES_PER_REPLAY),
    ("L5_grasp_robot0_robotview.gif",  "grasp",    FRAMES_PER_GRASP),
    ("L5_replay_birdview.gif",         "birdview", FRAMES_PER_REPLAY),
    ("L5_replay_robot0_robotview.gif", "robotview",FRAMES_PER_REPLAY),
]


def calc_low_var_ratio(arr: np.ndarray) -> float:
    """计算8x8块方差<5的比例（像素化指标）。"""
    h, w = arr.shape[:2]
    block_vars = []
    for y in range(0, h - 8, 8):
        for x in range(0, w - 8, 8):
            block_vars.append(arr[y:y+8, x:x+8, :].var())
    if not block_vars:
        return 1.0
    return sum(1 for v in block_vars if v < 5) / len(block_vars)


def scan_gif_quality(gif_path: Path) -> list[tuple[int, float, float]]:
    """扫描GIF所有帧的质量，返回[(frame_idx, mean, low_var_ratio)]。"""
    img = Image.open(gif_path)
    total = img.n_frames
    results = []
    for i in range(total):
        img.seek(i)
        frame = img.convert("RGB")
        arr = np.array(frame)
        mean = arr.mean()
        low_var = calc_low_var_ratio(arr)
        results.append((i, mean, low_var))
    return results


def select_best_frames(quality: list[tuple[int, float, float]], n_frames: int) -> list[int]:
    """从质量列表中选择n_frames个最佳帧（low_var<0.20的帧中均匀分布）。"""
    # 筛选正常帧
    normal = [(idx, mean, lv) for idx, mean, lv in quality if lv < 0.20]
    if not normal:
        # 所有帧都异常，选择low_var最低的n帧
        sorted_by_lv = sorted(quality, key=lambda x: x[2])
        return [x[0] for x in sorted_by_lv[:n_frames]]

    if len(normal) <= n_frames:
        return [x[0] for x in normal]

    # 在正常帧中均匀分布
    indices = []
    step = len(normal) / n_frames
    for i in range(n_frames):
        pos = int(i * step)
        indices.append(normal[pos][0])
    return indices


def main() -> int:
    # 清理旧照片
    if OUT_DIR.exists():
        import shutil
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    issues = []

    for gif_name, view, n_frames in GIF_LIST:
        gif_path = GIF_DIR / gif_name
        if not gif_path.exists():
            print(f"[SKIP] {gif_name} 不存在")
            continue

        level = gif_name.split("_")[0]
        level_dir = OUT_DIR / level
        level_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n=== {gif_name} ===")
        quality = scan_gif_quality(gif_path)
        n_normal = sum(1 for _, _, lv in quality if lv < 0.20)
        n_abnormal = len(quality) - n_normal
        print(f"  总帧数: {len(quality)}, 正常: {n_normal}, 异常: {n_abnormal}")

        if n_abnormal > 0:
            abnormal_frames = [(idx, mean, lv) for idx, mean, lv in quality if lv >= 0.20]
            print(f"  异常帧: {[(idx, f'lv={lv:.2f}') for idx, _, lv in abnormal_frames[:5]]}")
            if n_normal == 0:
                issues.append(f"{level}/{view}: 全部{len(quality)}帧异常！")
                print(f"  [WARNING] 所有帧都异常！将选择质量最好的{n_frames}帧")

        # 选择最佳帧
        best_indices = select_best_frames(quality, n_frames)
        print(f"  选中帧: {best_indices}")

        # 保存选中帧
        img = Image.open(gif_path)
        for i, idx in enumerate(best_indices):
            img.seek(idx)
            frame = img.convert("RGB")
            arr = np.array(frame)
            lv = calc_low_var_ratio(arr)
            out_path = level_dir / f"{level}_{view}_{i+1:02d}.png"
            frame.save(out_path, "PNG")
            total += 1
            status = "OK" if lv < 0.20 else "WARN"
            print(f"    帧{idx:4d} (mean={arr.mean():.1f}, lv={lv:.2f}) -> {out_path.name} [{status}]")

    print(f"\n=== 完成：共抽取 {total} 张照片 ===")
    if issues:
        print(f"\n[需处理的问题]:")
        for issue in issues:
            print(f"  - {issue}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

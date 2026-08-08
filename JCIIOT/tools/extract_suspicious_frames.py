"""从回放 GIF 中提取指定原始轨迹帧附近的画面保存为 PNG。

GIF 是抽帧后的(step = max(1, n_frames // 300)),需要反推 GIF 帧索引。
还会提取前后各 2 帧用于对比。
"""
import json
from pathlib import Path

from PIL import Image

GIF_DIR = Path(__file__).parent.parent / "submission" / "replay_gifs"
TRAJ_DIR = Path(__file__).parent.parent.parent / "submission" / "trajectories"
OUT_DIR = GIF_DIR / "suspicious_frames"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_frames(gif_path: Path, target_original_frame: int, n_frames: int,
                   label: str, context: int = 2):
    """从 GIF 提取最接近 target_original_frame 的帧及前后 context 帧。

    GIF 抽帧: step = max(1, n_frames // 300), GIF帧 = original // step
    末尾还有 5 个暂停帧(重复最后一帧)。
    """
    step = max(1, n_frames // 300)
    target_gif_frame = target_original_frame // step
    print(f"\n=== {label} ===")
    print(f"  原始帧: {target_original_frame}, 轨迹总帧: {n_frames}")
    print(f"  抽帧step: {step}, 对应GIF帧: {target_gif_frame}")
    print(f"  GIF: {gif_path.name}")

    img = Image.open(gif_path)
    total_gif_frames = img.n_frames
    print(f"  GIF总帧数: {total_gif_frames}")

    # 提取 target 及前后 context 帧
    frames_to_extract = list(range(
        max(0, target_gif_frame - context),
        min(total_gif_frames, target_gif_frame + context + 1)
    ))

    saved = []
    for gif_idx in frames_to_extract:
        img.seek(gif_idx)
        frame = img.convert("RGB")
        # 标注: 原始帧号 + GIF帧号
        orig_frame = gif_idx * step
        out_name = f"{label}_gif{gif_idx:04d}_orig{orig_frame:05d}.png"
        out_path = OUT_DIR / out_name
        frame.save(out_path)
        saved.append((out_path, orig_frame, gif_idx))
        print(f"  [SAVED] {out_name}")

    return saved


def main():
    # L2: 帧275, green_tote_b01_lower Y方向跳0.234m
    l2_traj = TRAJ_DIR / "L2_FactorySorting3_3FO3ERRPH7X9.json"
    l2_data = json.loads(l2_traj.read_text(encoding="utf-8"))
    l2_nframes = len(l2_data["frames"])
    # physics_audit 说 worst_jump_frame=275, 对象 green_tote_b01_lower
    # L2全程GIF: birdview + robotview 都有
    for cam in ["birdview", "robot0_robotview"]:
        gif = GIF_DIR / f"L2_replay_{cam}.gif"
        if gif.exists():
            extract_frames(gif, 275, l2_nframes, f"L2_{cam}")
        else:
            print(f"[SKIP] {gif.name} 不存在")

    # L5: 帧4977, white_tote_b01_left_front Z方向跳-0.232m
    l5_traj = TRAJ_DIR / "L5_FactorySorting9_3FO3ERT2C5FP.json"
    l5_data = json.loads(l5_traj.read_text(encoding="utf-8"))
    l5_nframes = len(l5_data["frames"])
    for cam in ["birdview", "robot0_robotview"]:
        gif = GIF_DIR / f"L5_replay_{cam}.gif"
        if gif.exists():
            extract_frames(gif, 4977, l5_nframes, f"L5_{cam}")
        else:
            print(f"[SKIP] {gif.name} 不存在")

    print(f"\n=== 完成,输出目录: {OUT_DIR} ===")
    print("请打开 PNG 文件查看,重点对比物体位置是否有瞬移")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""批量生成 5 关轨迹的真实仿真回放 GIF（不依赖 Streamlit UI）。

复用官方 RobosuiteBackend.replay_trajectory + app.py 中的 grasp 段推断与
_save_gif 逻辑，对每个 L*_FactorySorting*.json 生成：
  - birdview  全程回放 GIF
  - robot0_robotview  全程回放 GIF
  - robot0_robotview  抓取片段 GIF（grasp_start -> grasp_end）

用法（在 DSW 或本地 Linux + MuJoCo/robosuite 环境运行）：
    cd JCIIOT
    python tools/batch_generate_replay_gifs.py \
        --traj-dir ../submission/trajectories \
        --out-dir  ../submission/replay_gifs

也可只生成某一关：
    python tools/batch_generate_replay_gifs.py --only L2,L5
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

# ---- 复用 app.py 里的 grasp 段推断逻辑（内联，避免 import streamlit）----
def infer_grasp_replay_range(json_path: Path):
    """从轨迹 JSON 推断 grasp 片段起止帧（start, end_exclusive, object_name）。"""
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    frames = data.get("frames", [])
    if len(frames) < 2:
        return None

    events = data.get("events", [])
    if isinstance(events, list):
        clean_events = []
        for event in events:
            if not isinstance(event, dict):
                continue
            try:
                frame = int(event.get("frame"))
            except Exception:
                continue
            if 0 <= frame < len(frames):
                clean_events.append((frame, event))
        clean_events.sort(key=lambda item: item[0])

        for start_frame, start_event in clean_events:
            if start_event.get("name") != "grasp_start":
                continue
            for end_frame, end_event in clean_events:
                if end_frame < start_frame:
                    continue
                if end_event.get("name") != "grasp_end":
                    continue
                obj_name = (
                    start_event.get("object_name")
                    or end_event.get("object_name")
                    or start_event.get("source")
                    or "grasp"
                )
                return start_frame, min(len(frames), end_frame + 1), str(obj_name)

    # 旧文件回退到启发式：取首个有明显抬升的物体
    object_names = data.get("object_names", [])
    if not object_names:
        return None

    best = None
    for obj_name in object_names:
        first = None
        for f in frames:
            pos = f.get("object_positions", {}).get(obj_name)
            if pos and len(pos) >= 3:
                first = (float(pos[0]), float(pos[1]), float(pos[2]))
                break
        if first is None:
            continue

        x0, y0, z0 = first
        max_score = 0.0
        trigger_idx = None
        move_idx = None
        for idx, f in enumerate(frames):
            pos = f.get("object_positions", {}).get(obj_name)
            if not pos or len(pos) < 3:
                continue
            dx = float(pos[0]) - x0
            dy = float(pos[1]) - y0
            dz = float(pos[2]) - z0
            xy = float((dx * dx + dy * dy) ** 0.5)
            score = xy + max(0.0, dz) * 2.0
            if score > max_score:
                max_score = score
            if trigger_idx is None and dz > 0.03:
                trigger_idx = idx
            if move_idx is None and xy > 0.20:
                move_idx = idx

        if trigger_idx is None:
            trigger_idx = move_idx
        if trigger_idx is None or max_score < 0.05:
            continue
        candidate = (max_score, obj_name, trigger_idx, move_idx)
        if best is None or candidate[0] > best[0]:
            best = candidate

    if best is None:
        return None

    _, obj_name, trigger_idx, move_idx = best
    start = max(0, trigger_idx - 30)
    end = min(len(frames), trigger_idx + 180)
    return start, end, str(obj_name)


# ---- 复用 app.py 的 _save_gif 逻辑（末尾 2s 暂停，抽样到 60 帧）----
def save_gif(frames: list, path: Path) -> None:
    """把 numpy 帧序列保存为 GIF，末尾暂停 2s。"""
    from PIL import Image

    if not frames:
        return
    display = frames[:: max(1, len(frames) // 60)]
    _last = display[-1]
    _pause_frames = [Image.fromarray(_last)] * 8  # 8 * 250ms = 2s
    _all_frames = [Image.fromarray(f) for f in display] + _pause_frames
    _all_frames[0].save(
        path, format="GIF", save_all=True,
        append_images=_all_frames[1:], duration=50, loop=0,
    )


# 从文件名推断 env_name，例如 L1_FactorySorting1_3FO3ERFHISEM.json -> FactorySorting1_3FO3ERFHISEM
_ENV_RE = re.compile(r"L\d+_(FactorySorting\d+_\w+)\.json", re.IGNORECASE)


def env_name_from_path(json_path: Path) -> str | None:
    m = _ENV_RE.search(json_path.name)
    if m:
        return m.group(1)
    # 回退：读 JSON 的 robot_model 字段
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        env = data.get("robot_model")
        if env and "FactorySorting" in str(env):
            return str(env)
    except Exception:
        pass
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="批量生成轨迹回放 GIF")
    ap.add_argument("--traj-dir", default="../submission/trajectories",
                    help="轨迹 JSON 所在目录")
    ap.add_argument("--out-dir", default="../submission/replay_gifs",
                    help="GIF 输出目录")
    ap.add_argument("--only", default="",
                    help="只处理指定关卡，逗号分隔，如 L2,L5")
    ap.add_argument("--cameras", default="birdview,robot0_robotview",
                    help="相机视角，逗号分隔")
    ap.add_argument("--skip-grasp", action="store_true",
                    help="跳过 grasp 片段 GIF（只生成全程回放）")
    args = ap.parse_args()

    traj_dir = Path(args.traj_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    only_set = {x.strip().upper() for x in args.only.split(",") if x.strip()} if args.only else None
    cameras = [c.strip() for c in args.cameras.split(",") if c.strip()]

    json_files = sorted(traj_dir.glob("L*_FactorySorting*.json"))
    if not json_files:
        print(f"[ERROR] 未找到轨迹文件: {traj_dir}/L*_FactorySorting*.json")
        return 1

    # 延迟导入 RobosuiteBackend（需要 robosuite/mujoco 环境）
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import robot_agent.workflows  # noqa: F401 — 触发 qM/mj_fullM 兼容补丁
        from robot_agent.environments import RobosuiteBackend  # type: ignore
    except Exception as exc:
        print(f"[ERROR] 无法导入 RobosuiteBackend（需 MuJoCo/robosuite 环境）: {exc}")
        return 2

    total_generated = 0
    for json_path in json_files:
        level = json_path.name.split("_")[0].upper()  # L1 / L2 ...
        if only_set and level not in only_set:
            continue

        env_name = env_name_from_path(json_path)
        if not env_name:
            print(f"[SKIP] 无法推断 env_name: {json_path.name}")
            continue

        print(f"\n=== {level}  {json_path.name}  env={env_name} ===")

        # 全程回放：每个相机一个 GIF
        for cam in cameras:
            gif_path = out_dir / f"{level}_replay_{cam}.gif"
            if gif_path.exists():
                print(f"  [EXISTS] {gif_path.name}（跳过，删除后可重生成）")
                continue
            print(f"  [FULL ] {cam} -> {gif_path.name} ...")
            try:
                backend = RobosuiteBackend(
                    env_name=env_name, camera=cam,
                    drive_mode="direct", headless=True,
                )
                backend.reset()
                backend.replay_trajectory(json_path, gif_path, camera=cam)
                backend.close()
                total_generated += 1
                print(f"          OK ({gif_path.stat().st_size // 1024} KB)")
            except Exception as exc:
                print(f"          FAIL: {exc}")

        # grasp 片段：仅 robot0_robotview（胸部相机特写）
        if not args.skip_grasp:
            grasp_range = infer_grasp_replay_range(json_path)
            if grasp_range is None:
                print(f"  [GRASP] 无法推断 grasp 片段，跳过")
                continue
            frame_start, frame_end, grasp_obj = grasp_range
            gif_path = out_dir / f"{level}_grasp_robot0_robotview.gif"
            if gif_path.exists():
                print(f"  [EXISTS] {gif_path.name}（跳过）")
                continue
            print(f"  [GRASP] robot0_robotview frames {frame_start}-{frame_end-1} ({grasp_obj}) -> {gif_path.name} ...")
            try:
                backend = RobosuiteBackend(
                    env_name=env_name, camera="robot0_robotview",
                    drive_mode="direct", headless=True,
                )
                backend.reset()
                backend.replay_trajectory(
                    json_path, gif_path, camera="robot0_robotview",
                    frame_start=frame_start, frame_end=frame_end,
                )
                backend.close()
                total_generated += 1
                print(f"          OK ({gif_path.stat().st_size // 1024} KB)")
            except Exception as exc:
                print(f"          FAIL: {exc}")

    print(f"\n=== 完成：共生成 {total_generated} 个 GIF，输出目录 {out_dir} ===")
    print("自检要点：肉眼逐关检查是否有瞬移/隔空放物/物体瞬贴桌面。")
    print("重点关：L2（worst_jump=0.249）、L5（worst_jump=0.248），接近 warn 阈值 0.25。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

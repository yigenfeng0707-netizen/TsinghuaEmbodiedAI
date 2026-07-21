"""Robust headless level runner (self-made).

Strategy for the known-weak official BC checkpoint (per the 07-17 teacher
briefing: "official Checkpoint robustness insufficient"): for each level, try
the official grasp base pose, and on pick-up failure retry with small
perturbations of the base XY / yaw (a temp, permitted task_config variant) until
grasp succeeds or attempts are exhausted. Records a trajectory JSON per attempt
and a per-level summary.

Each level attempt runs in a subprocess with a hard wall-clock timeout so a slow
CPU rollout cannot wedge the batch.

Run:
    PYTHONPATH=src python tools/run_level_robust.py L1 L2 L3 L4 L5
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from preflight import run_checks  # noqa: E402


def map_paths(level: str) -> tuple[Path, Path]:
    suffixes = {
        "L1": "1_3fo3erfhisem", "L2": "3_3fo3errph7x9", "L3": "5_3fo3ertpxeut",
        "L4": "7_3fo3erfky9rn", "L5": "9_3fo3ert2c5fp",
    }
    maps = ROOT / "robosuite/robosuite/environments/factory_sorting/generated_maps"
    stem = f"factory_sorting_{suffixes[level.upper()]}_scene_regenerated"
    return maps / f"{stem}_semantic_map.json", maps / f"{stem}_occupancy_grid.npy"


def _attempt(level, grasp_pose, record_dir, timeout):
    """Run one level attempt in a subprocess; return (success, report_or_none, err)."""
    cfg = json.loads((ROOT / "knowledge/task_config.json").read_text(encoding="utf-8"))
    # Override the official grasp pose for this level's source with the perturbation.
    source = next(t["source"] for t in cfg["tasks"] if t["level"] == level)
    cfg["grasp_poses"][source] = {
        "pos": [float(grasp_pose[0]), float(grasp_pose[1]), 0.0],
        "yaw": float(grasp_pose[2]),
    }
    tmp = Path(tempfile.gettempdir()) / f"jc_iot_cfg_{level}.json"
    tmp.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")

    record = record_dir / f"{level}.json"
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"),
           "JCIOT_LEVEL": level, "JCIOT_CFG": str(tmp), "JCIOT_RECORD": str(record)}
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "_run_one_level.py")],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=timeout,
    )
    report = None
    if record.exists():
        try:
            report = json.loads(record.read_text(encoding="utf-8"))
        except Exception:
            report = None
    err = proc.stderr[-1500:] if proc.returncode != 0 else ""
    return proc.returncode == 0, report, err


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("levels", nargs="+", choices=["L1", "L2", "L3", "L4", "L5"])
    ap.add_argument("--record-dir", type=Path, default=ROOT / "recordings" / "robust")
    ap.add_argument("--timeout", type=int, default=420, help="per-attempt wall-clock seconds")
    ap.add_argument("--max-attempts", type=int, default=8)
    args = ap.parse_args()

    failures = [c for c in run_checks(ROOT) if c.required and not c.ok]
    if failures:
        for c in failures:
            print(f"Preflight blocked: {c.name}: {c.detail}", file=sys.stderr)
        return 2

    args.record_dir.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((ROOT / "knowledge/task_config.json").read_text(encoding="utf-8"))

    # Perturbation grid around the official pose.
    offsets = [(0.0, 0.0, 0.0), (0.05, 0.0, 0.0), (-0.05, 0.0, 0.0),
               (0.0, 0.05, 0.0), (0.0, -0.05, 0.0), (0.08, 0.0, 0.03),
               (-0.08, 0.0, -0.03), (0.10, 0.10, 0.0)]

    summary = {}
    for level in args.levels:
        source = next(t["source"] for t in cfg["tasks"] if t["level"] == level)
        base = cfg["grasp_poses"][source]
        base_xy = base["pos"][:2]
        base_yaw = base["yaw"]
        print(f"\n=== {level} (source={source}) base_pose=({base_xy}, yaw={base_yaw}) ===", flush=True)
        success = False
        used_pose = None
        for i, (dx, dy, dyaw) in enumerate(offsets[:args.max_attempts]):
            pose = [base_xy[0] + dx, base_xy[1] + dy, base_yaw + dyaw]
            print(f"  attempt {i+1}: pose=({pose[0]:.3f},{pose[1]:.3f},yaw={pose[2]:.4f})", flush=True)
            t0 = time.time()
            try:
                ok, report, err = _attempt(level, pose, args.record_dir / f"attempt_{i+1}", args.timeout)
            except subprocess.TimeoutExpired:
                print(f"    TIMEOUT after {args.timeout}s", flush=True)
                ok, report, err = False, None, "timeout"
            dt = time.time() - t0
            print(f"    -> {'OK' if ok else 'fail'} ({dt:.0f}s)", flush=True)
            if ok:
                success = True
                used_pose = pose
                # Copy successful trajectory to canonical level file.
                src = args.record_dir / f"attempt_{i+1}" / f"{level}.json"
                if src.exists():
                    (args.record_dir / f"{level}.json").write_text(
                        src.read_text(encoding="utf-8"), encoding="utf-8")
                break
        summary[level] = {"success": success, "used_pose": used_pose}
        print(f"  {level} summary: success={success}", flush=True)

    (args.record_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n=== BATCH SUMMARY ===")
    for lv, s in summary.items():
        print(f"  {lv}: {'PASS' if s['success'] else 'FAIL'}")
    return 0 if all(s["success"] for s in summary.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

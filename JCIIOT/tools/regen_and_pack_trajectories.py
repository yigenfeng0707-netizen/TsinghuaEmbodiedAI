#!/usr/bin/env python3
"""Regenerate official-template trajectories for L1-L5 and pack Biendata zip.

Run from JCIIOT/ with local package paths (see run_level.py):
  python tools/regen_and_pack_trajectories.py
  python tools/regen_and_pack_trajectories.py --levels L1 L3
  python tools/regen_and_pack_trajectories.py --pack-only
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT_DIR = REPO / "submission" / "trajectories"
VAL_DIR = REPO / "submission" / "biendata_validation"

PREFERRED = {
    "L1": "L1_FactorySorting1_3FO3ERFHISEM.json",
    "L2": "L2_FactorySorting3_3FO3ERRPH7X9.json",
    "L3": "L3_FactorySorting5_3FO3ERTPXEUT.json",
    "L4": "L4_FactorySorting7_3FO3ERFKY9RN.json",
    "L5": "L5_FactorySorting9_3FO3ERT2C5FP.json",
}


def _setup_paths() -> None:
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(ROOT / "robosuite"))
    sys.path.insert(0, str(ROOT / "robosuite" / "robosuite"))
    sys.path.insert(0, str(ROOT / "robomimic"))


def _map_paths(level: str) -> tuple[Path, Path]:
    suffixes = {
        "L1": "1_3fo3erfhisem",
        "L2": "3_3fo3errph7x9",
        "L3": "5_3fo3ertpxeut",
        "L4": "7_3fo3erfky9rn",
        "L5": "9_3fo3ert2c5fp",
    }
    stem = f"factory_sorting_{suffixes[level]}_scene_regenerated"
    maps = ROOT / "robosuite/robosuite/environments/factory_sorting/generated_maps"
    return maps / f"{stem}_semantic_map.json", maps / f"{stem}_occupancy_grid.npy"


def run_level(level: str, *, force: bool = False) -> Path:
    _setup_paths()
    import robosuite as _rs  # noqa: F401
    from robot_agent.environments import robosuite_backend  # noqa: F401
    import robosuite.environments.factory_sorting.load_factory_sorting_evalization as _eval
    from robot_agent.core.map_loader import load_map_files
    from robot_agent.core.scene_context import SceneContext
    from robot_agent.environments import RobosuiteBackend
    from robot_agent.workflows import ChampionTransportFlow

    # Headless renderer patch (same as tools/run_level.py)
    if not hasattr(_eval, "_original_make_factory_sorting_env_kwargs"):
        _eval._original_make_factory_sorting_env_kwargs = _eval.make_factory_sorting_env_kwargs

        def _patched(args):
            kwargs = _eval._original_make_factory_sorting_env_kwargs(args)
            kwargs["renderer"] = "mujoco"
            kwargs["has_renderer"] = False
            kwargs["has_offscreen_renderer"] = True
            return kwargs

        _eval.make_factory_sorting_env_kwargs = _patched

    semantic_map, occupancy_grid = _map_paths(level)
    scene, grid = load_map_files(semantic_map, occupancy_grid)
    context = SceneContext.from_semantic_map(scene)
    task_config = json.loads((ROOT / "knowledge/task_config.json").read_text(encoding="utf-8"))
    task = next(t for t in task_config["tasks"] if t["level"] == level)

    out_path = OUT_DIR / PREFERRED[level]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Never clobber a known-good trajectory with a failed local run unless forced.
    backup_path = out_path.with_suffix(out_path.suffix + ".bak")
    if out_path.exists() and not force:
        shutil.copy2(out_path, backup_path)

    backend = RobosuiteBackend(
        env_name=task["env_name"], camera="birdview", drive_mode="direct", headless=True,
    )
    try:
        backend.reset()
        backend._scene_context = context
        if hasattr(backend, "enable_physics_grasp"):
            try:
                backend.enable_physics_grasp()
            except Exception:
                pass
        backend.start_recording()
        report = ChampionTransportFlow(
            backend=backend,
            scene_context=context,
            grid=grid,
            task_config_path=ROOT / "knowledge/task_config.json",
        ).execute_level(level)
        if not report.success and backup_path.exists() and not force:
            shutil.copy2(backup_path, out_path)
            print(
                f"[{level}] RUN FAILED ({report.failed_step}); restored previous trajectory from {backup_path.name}",
                flush=True,
            )
            return out_path
        saved = backend.save_trajectory(out_path)
        meta_path = OUT_DIR / f"{level}_run_report.json"
        meta_path.write_text(
            json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[{level}] success={report.success} failed={report.failed_step} traj={saved}")
    finally:
        backend.close()
    return out_path


def pack_zip() -> Path:
    VAL_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = VAL_DIR / "SOP-MapGuard_validation_trajectories.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for level, name in PREFERRED.items():
            src = OUT_DIR / name
            if not src.exists():
                raise FileNotFoundError(f"missing {src}")
            zf.write(src, arcname=name)
    print(f"packed {zip_path} ({zip_path.stat().st_size} bytes)")
    return zip_path


def score() -> None:
    from score_trajectories_offline import main as score_main
    sys.argv = ["score_trajectories_offline.py", str(OUT_DIR)]
    score_main()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", nargs="*", default=["L1", "L2", "L3", "L4", "L5"])
    ap.add_argument("--pack-only", action="store_true")
    ap.add_argument("--skip-score", action="store_true")
    ap.add_argument("--force", action="store_true", help="Overwrite even if the new run fails")
    args = ap.parse_args()

    if not args.pack_only:
        for level in args.levels:
            level = level.upper()
            try:
                run_level(level, force=args.force)
            except Exception as exc:
                print(f"[{level}] RUN FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
                # Keep going for remaining levels; pack whatever is valid.
                continue

    pack_zip()
    if not args.skip_score:
        score()
    # upload hint
    readme = VAL_DIR / "README_UPLOAD.txt"
    readme.write_text(
        "Upload ONLY this zip to Biendata validation.\n"
        "Contents: five L*_FactorySorting*.json (flat, no subdirs).\n"
        "Do NOT include L1.json-L5.json or summary.json.\n"
        "Suggested note (<=40 chars): SOP-MapGuard L1-L5 retarget\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())

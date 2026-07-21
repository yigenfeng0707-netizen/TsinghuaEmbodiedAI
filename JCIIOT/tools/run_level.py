"""Self-made headless level runner.

Reuses the official ChampionTransportFlow + RobosuiteBackend, but patches the
competition eval env factory so the grasp policy runs with MuJoCo's offscreen
renderer (renderer="mujoco", has_renderer=False) instead of the windowed
"mjviewer" backend, which hangs on a headless machine.

Run:
    PYTHONPATH=src python tools/run_level.py L1 --record-dir recordings/task1_l1
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "robosuite"))
sys.path.insert(0, str(ROOT / "robosuite" / "robosuite"))
sys.path.insert(0, str(ROOT / "robomimic"))

import robosuite as _rs  # noqa: F401  (namespace-package fix performed in backend)
from robot_agent.environments import robosuite_backend  # noqa: F401  (applies __file__ monkeypatch)

from robot_agent.core.map_loader import load_map_files
from robot_agent.core.scene_context import SceneContext
from robot_agent.workflows import ChampionTransportFlow
from preflight import run_checks

# ── headless-safe renderer patch ──────────────────────────────
# The official grasp pipeline (load_factory_sorting_evalization.make_eval_env)
# hardcodes renderer="mjviewer", which blocks on headless boxes. Force the
# offscreen MuJoCo backend so grasp inference runs without a GL window.
import robosuite.environments.factory_sorting.load_factory_sorting_evalization as _eval


def _patched_make_factory_sorting_env_kwargs(args):
    kwargs = _eval._original_make_factory_sorting_env_kwargs(args)
    kwargs["renderer"] = "mujoco"
    kwargs["has_renderer"] = False
    kwargs["has_offscreen_renderer"] = True
    return kwargs


if not hasattr(_eval, "_original_make_factory_sorting_env_kwargs"):
    _eval._original_make_factory_sorting_env_kwargs = _eval.make_factory_sorting_env_kwargs
    _eval.make_factory_sorting_env_kwargs = _patched_make_factory_sorting_env_kwargs

    _orig_grasp = _eval.run_factory_sorting_grasp_in_wrapped_env

    def _instrumented_grasp(env, policy, **kw):
        import time as _t
        raw = _eval.base_robosuite_env(env)
        if hasattr(policy, "start_episode"):
            policy.start_episode()
        obs = _eval.current_wrapped_policy_obs(env)
        _t0 = _t.time()
        steps = kw.get("eval_steps", 360)
        print(f"[GRASP] starting {steps} steps", flush=True)
        for step in range(steps):
            act = policy(ob=obs)
            obs, r, done, _ = env.step(act)
            if step % 20 == 0:
                print(f"[GRASP] step {step}/{steps} t={_t.time()-_t0:.1f}s", flush=True)
            if done:
                print(f"[GRASP] done at step {step}", flush=True)
                break
        print(f"[GRASP] loop finished t={_t.time()-_t0:.1f}s", flush=True)
        return {"success": False}

    _eval.run_factory_sorting_grasp_in_wrapped_env = _instrumented_grasp


def map_paths(level: str) -> tuple[Path, Path]:
    suffixes = {
        "L1": "1_3fo3erfhisem",
        "L2": "3_3fo3errph7x9",
        "L3": "5_3fo3ertpxeut",
        "L4": "7_3fo3erfky9rn",
        "L5": "9_3fo3ert2c5fp",
    }
    try:
        suffix = suffixes[level.upper()]
    except KeyError as exc:
        raise ValueError("level must be L1, L2, L3, L4, or L5") from exc
    maps = ROOT / "robosuite/robosuite/environments/factory_sorting/generated_maps"
    stem = f"factory_sorting_{suffix}_scene_regenerated"
    return maps / f"{stem}_semantic_map.json", maps / f"{stem}_occupancy_grid.npy"


def main() -> int:
    parser = argparse.ArgumentParser(description="Headless rules-compliant contest level runner (self-made)")
    parser.add_argument("level", choices=["L1", "L2", "L3", "L4", "L5"])
    parser.add_argument("--record-dir", type=Path, help="Write the physical execution report as LEVEL.json here")
    args = parser.parse_args()

    failures = [c for c in run_checks(ROOT) if c.required and not c.ok]
    if failures:
        for c in failures:
            print(f"Preflight blocked: {c.name}: {c.detail}", file=sys.stderr)
        return 2

    from robot_agent.environments import RobosuiteBackend

    semantic_map, occupancy_grid = map_paths(args.level)
    scene, grid = load_map_files(semantic_map, occupancy_grid)
    context = SceneContext.from_semantic_map(scene)
    task_config = json.loads((ROOT / "knowledge/task_config.json").read_text(encoding="utf-8"))
    task = next(t for t in task_config["tasks"] if t["level"] == args.level)
    backend = RobosuiteBackend(
        env_name=task["env_name"], camera="birdview", drive_mode="direct", headless=True,
    )
    try:
        backend.reset()
        report = ChampionTransportFlow(
            backend=backend,
            scene_context=context,
            grid=grid,
            task_config_path=ROOT / "knowledge/task_config.json",
        ).execute_level(args.level)
    finally:
        backend.close()

    if args.record_dir is not None:
        args.record_dir.mkdir(parents=True, exist_ok=True)
        record_path = args.record_dir / f"{report.level}.json"
        record_path.write_text(
            json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Recorded physical execution: {record_path}")
    for step in report.steps:
        print(f"{'PASS' if step.success else 'FAIL'} {step.skill_name}: {step.message}")
    return 0 if report.success else 1


if __name__ == "__main__":
    raise SystemExit(main())

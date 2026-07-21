"""Single-level driver invoked by run_level_robust.py as a subprocess.

Reads JCIOT_CFG (perturbed task_config path) and JCIOT_LEVEL / JCIOT_RECORD
from the environment, runs one ChampionTransportFlow level headless, and writes
the trajectory JSON to JCIOT_RECORD. The grasp eval env is forced to the
offscreen MuJoCo renderer so it runs without a GL window.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "src"), str(ROOT / "robosuite"),
          str(ROOT / "robosuite" / "robosuite"), str(ROOT / "robomimic")):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402
import robosuite as _rs  # noqa: E401
from robot_agent.environments import RobosuiteBackend  # noqa: E401
import robosuite.environments.factory_sorting.load_factory_sorting_evalization as _eval  # noqa: E401

_orig = _eval.make_factory_sorting_env_kwargs


def _patched(args):
    k = _orig(args)
    k["renderer"] = "mujoco"
    k["has_renderer"] = False
    k["has_offscreen_renderer"] = True
    return k


_eval.make_factory_sorting_env_kwargs = _patched

from robot_agent.core.map_loader import load_map_files  # noqa: E402
from robot_agent.core.scene_context import SceneContext  # noqa: E402
from robot_agent.workflows import ChampionTransportFlow  # noqa: E402


def _map_paths(level: str) -> tuple[Path, Path]:
    suffixes = {
        "L1": "1_3fo3erfhisem", "L2": "3_3fo3errph7x9", "L3": "5_3fo3ertpxeut",
        "L4": "7_3fo3erfky9rn", "L5": "9_3fo3ert2c5fp",
    }
    maps = ROOT / "robosuite/robosuite/environments/factory_sorting/generated_maps"
    stem = f"factory_sorting_{suffixes[level.upper()]}_scene_regenerated"
    return maps / f"{stem}_semantic_map.json", maps / f"{stem}_occupancy_grid.npy"


def main() -> int:
    level = os.environ["JCIOT_LEVEL"]
    cfg_path = os.environ["JCIOT_CFG"]
    record = Path(os.environ["JCIOT_RECORD"])

    semantic_map, occupancy_grid = _map_paths(level)
    scene, grid = load_map_files(semantic_map, occupancy_grid)
    context = SceneContext.from_semantic_map(scene)
    task_config = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    task = next(t for t in task_config["tasks"] if t["level"] == level)
    backend = RobosuiteBackend(
        env_name=task["env_name"], camera="birdview", drive_mode="direct", headless=True)
    try:
        backend.reset()
        report = ChampionTransportFlow(
            backend=backend, scene_context=context, grid=grid,
            task_config_path=cfg_path,
        ).execute_level(level)
    finally:
        backend.close()

    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return 0 if report.success else 1


if __name__ == "__main__":
    raise SystemExit(main())

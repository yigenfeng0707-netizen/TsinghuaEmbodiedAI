"""
Stage 264: 测试 ChampionTransportFlow 完整流程（navigate+grasp+lift+transport+place）

5 关卡：
- L1: task_index=0, env=FactorySorting1_3FO3ERFHISEM
- L2: task_index=1, env=FactorySorting3_3FO3ERRPH7X9
- L3: task_index=2, env=FactorySorting5_3FO3ERTPXEUT
- L4: task_index=3, env=FactorySorting7_3FO3ERFKY9RN
- L5: task_index=4, env=FactorySorting9_3FO3ERT2C5FP
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dsw_remote import DswRemote


REMOTE_SCRIPT = r"""
import os, sys, math, gc, time, json
os.environ.setdefault("MUJOCO_GL", "egl")
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

# 配置路径
APP_DIR = "/mnt/workspace/JCIIOT_repo/JCIIOT"
sys.path.insert(0, APP_DIR + "/src")
sys.path.insert(0, APP_DIR)
sys.path.insert(0, APP_DIR + "/robosuite/robosuite")
sys.path.insert(0, APP_DIR + "/robomimic")

import warnings
warnings.filterwarnings("ignore")
import logging
logging.getLogger("robosuite").setLevel(logging.ERROR)
logging.getLogger("robot_agent").setLevel(logging.WARNING)

import numpy as np

print("=" * 70)
print("STAGE 264: ChampionTransportFlow 完整流程测试")
print("=" * 70)

# 5 关卡配置
LEVELS = [
    {"level": "L1", "task_index": 0, "env": "FactorySorting1_3FO3ERFHISEM",
     "prefix": "factory_sorting_1_3fo3erfhisem", "max_score": 10},
    {"level": "L2", "task_index": 1, "env": "FactorySorting3_3FO3ERRPH7X9",
     "prefix": "factory_sorting_3_3fo3errph7x9", "max_score": 15},
    {"level": "L3", "task_index": 2, "env": "FactorySorting5_3FO3ERTPXEUT",
     "prefix": "factory_sorting_5_3fo3ertpxeut", "max_score": 20},
    {"level": "L4", "task_index": 3, "env": "FactorySorting7_3FO3ERFKY9RN",
     "prefix": "factory_sorting_7_3fo3erfky9rn", "max_score": 25},
    {"level": "L5", "task_index": 4, "env": "FactorySorting9_3FO3ERT2C5FP",
     "prefix": "factory_sorting_9_3fo3ert2c5fp", "max_score": 30},
]

MAP_DIR = APP_DIR + "/robosuite/robosuite/environments/factory_sorting/generated_maps"


def build_flow_for_level(cfg):
    # build ChampionTransportFlow
    from robot_agent.environments.robosuite_backend import RobosuiteBackend
    from robot_agent.core.map_loader import load_map_files
    from robot_agent.core.scene_context import SceneContext
    from robot_agent.workflows.champion_transport import ChampionTransportFlow

    # 加载 map
    semantic_path = MAP_DIR + "/" + cfg["prefix"] + "_scene_regenerated_semantic_map.json"
    grid_path = MAP_DIR + "/" + cfg["prefix"] + "_scene_regenerated_occupancy_grid.npy"
    print(f"  semantic: {semantic_path}")
    print(f"  grid: {grid_path}")

    scene, grid = load_map_files(semantic_path, grid_path)
    scene_ctx = SceneContext.from_semantic_map(scene)

    # 构建 backend
    backend = RobosuiteBackend(
        env_name=cfg["env"],
        camera="birdview",
        drive_mode="direct",
        headless=True,
    )
    backend._scene_context = scene_ctx

    # 第一次 reset
    backend.reset()

    # 构建 object_map
    dynamic_input_object_map = {}
    raw_metadata = getattr(backend.env, "material_metadata", {}) or {}
    for obj_name, info in raw_metadata.items():
        if not isinstance(info, dict):
            continue
        port_name = str(info.get("port_name") or "")
        if port_name:
            dynamic_input_object_map[port_name] = obj_name
            if port_name.startswith("input_"):
                line_name = "line_" + port_name.split("_", 1)[1]
                dynamic_input_object_map[line_name] = obj_name
            elif port_name.startswith("line_"):
                input_name = "input_" + port_name.split("_", 1)[1]
                dynamic_input_object_map[input_name] = obj_name

    backend.set_physics_grasp_config(
        device="cpu",
        object_map=dynamic_input_object_map,
    )

    # 第二次 reset
    backend.reset()

    # 创建 flow
    flow = ChampionTransportFlow(
        backend=backend,
        scene_context=scene_ctx,
        grid=grid,
        task_config_path=APP_DIR + "/knowledge/task_config.json",
    )

    return flow, backend


def test_level(cfg):
    # test single level
    level = cfg["level"]
    print(f"\n{'#' * 60}")
    print(f"# {level}: {cfg['env']} (max_score={cfg['max_score']})")
    print(f"{'#' * 60}")

    flow = None
    backend = None
    try:
        flow, backend = build_flow_for_level(cfg)
        t0 = time.time()
        report = flow.execute_level(level)
        elapsed = time.time() - t0

        print(f"\n  [{level}] RESULT: success={report.success} elapsed={elapsed:.1f}s")
        print(f"  [{level}] failed_step: {report.failed_step}")
        print(f"  [{level}] source={report.source} target={report.target} obj={report.object_name}")
        print(f"  [{level}] steps:")
        for i, step in enumerate(report.steps):
            status = "OK" if step.success else "FAIL"
            print(f"    [{i+1}] {step.skill_name}: {status} - {step.message[:100]}")

        return report.success, elapsed, report.failed_step

    except Exception as e:
        import traceback
        print(f"\n  [{level}] EXCEPTION: {e}")
        traceback.print_exc()
        return False, 0, str(e)
    finally:
        if backend is not None:
            try:
                backend.close()
            except Exception:
                pass
        del flow
        del backend
        gc.collect()


# 测试所有关卡
results = {}
total_score = 0
for cfg in LEVELS:
    success, elapsed, failed_step = test_level(cfg)
    results[cfg["level"]] = {
        "success": success,
        "elapsed": elapsed,
        "max_score": cfg["max_score"],
        "failed_step": failed_step,
    }
    if success:
        total_score += cfg["max_score"]
    print(f"\n>>> {cfg['level']} 结果: {'SUCCESS' if success else 'FAILED'} (score={cfg['max_score'] if success else 0}, failed_step={failed_step})")

# 总结
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
for level, info in results.items():
    status = "OK" if info["success"] else "FAIL"
    score = info["max_score"] if info["success"] else 0
    failed = info["failed_step"] if not info["success"] else ""
    print(f"  {level}: {status} score={score}/{info['max_score']} elapsed={info['elapsed']:.1f}s {failed}")
print(f"\n  TOTAL: {total_score}/100")
print("=" * 70)
print("[DONE]")
"""


async def main():
    dsw = DswRemote()
    await dsw.connect()
    print("\n[Stage 264] 测试 ChampionTransportFlow 完整流程...")
    output = await dsw.execute_via_jupyter_api(REMOTE_SCRIPT, timeout=3600)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())

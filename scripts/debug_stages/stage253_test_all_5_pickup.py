"""
Stage 253: 测试全部 5 关卡 PickUpSkill + RobosuiteBackend.grasp_object_physics
- 验证 grasp + lift 都成功
- 使用 task_config.json 的 grasp_poses_by_level 配置

5 关卡：
- L1: env=FactorySorting1_3FO3ERFHISEM, obj=line_5_container_h01_near, base_pos=[8.0, 4.6, 0.0], yaw=-π, source=input_5
- L2: env=FactorySorting3_3FO3ERRPH7X9, obj=green_tote_b01_upper, base_pos=[12.81, 4.60, 0.0], yaw=-π, source=input_6
- L3: env=FactorySorting5_3FO3ERTPXEUT, obj=orange_tote_b01_upper, base_pos=[2.26, 5.29, 0.0], yaw=-π, source=input_6
- L4: env=FactorySorting7_3FO3ERFKY9RN, obj=blue_container_h01_back_upper, base_pos=[-8.95, 5.35, 0.0], yaw=-π, source=input_2
- L5: env=FactorySorting9_3FO3ERT2C5FP, obj=white_tote_b01_left_center, base_pos=[-13.73, 4.93, 0.0], yaw=-π, source=input_1
"""
import asyncio
import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dsw_remote import DswRemote


REMOTE_SCRIPT = r'''
import os, sys, math, gc, time
os.environ.setdefault("MUJOCO_GL", "egl")
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

sys.path.insert(0, "/mnt/workspace/JCIIOT_repo/JCIIOT/src")
sys.path.insert(0, "/mnt/workspace/JCIIOT_repo/JCIIOT")
sys.path.insert(0, "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite")
sys.path.insert(0, "/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic")

import warnings
warnings.filterwarnings("ignore")
import logging
logging.getLogger("robosuite").setLevel(logging.ERROR)
logging.getLogger("robot_agent").setLevel(logging.WARNING)

import numpy as np

print("=" * 70)
print("STAGE 253: 测试全部 5 关卡 PickUpSkill")
print("=" * 70)

from robot_agent.environments.robosuite_backend import RobosuiteBackend
from robot_agent.skills.pick_up import PickUpSkill
from robot_agent.core.types import ExecutionContext

# 5 关卡配置
LEVELS = [
    {"level": "L1", "env": "FactorySorting1_3FO3ERFHISEM", "obj": "line_5_container_h01_near",
     "pos": [8.0, 4.6], "yaw": -math.pi, "source": "input_5", "line": "line_5", "max_score": 10},
    {"level": "L2", "env": "FactorySorting3_3FO3ERRPH7X9", "obj": "green_tote_b01_upper",
     "pos": [12.81, 4.60], "yaw": -math.pi, "source": "input_6", "line": "line_6", "max_score": 15},
    {"level": "L3", "env": "FactorySorting5_3FO3ERTPXEUT", "obj": "orange_tote_b01_upper",
     "pos": [2.26, 5.29], "yaw": -math.pi, "source": "input_6", "line": "line_6", "max_score": 20},
    {"level": "L4", "env": "FactorySorting7_3FO3ERFKY9RN", "obj": "blue_container_h01_back_upper",
     "pos": [-8.95, 5.35], "yaw": -math.pi, "source": "input_2", "line": "line_2", "max_score": 25},
    {"level": "L5", "env": "FactorySorting9_3FO3ERT2C5FP", "obj": "white_tote_b01_left_center",
     "pos": [-13.73, 4.93], "yaw": -math.pi, "source": "input_1", "line": "line_1", "max_score": 30},
]


def test_level(cfg):
    """测试单个关卡的 PickUpSkill"""
    level = cfg["level"]
    print(f"\n{'#' * 60}")
    print(f"# {level}: {cfg['obj']} source={cfg['source']}")
    print(f"# base_pos={cfg['pos']} yaw={cfg['yaw']:.4f}")
    print(f"{'#' * 60}")

    backend = None
    try:
        # 1. 创建 backend
        backend = RobosuiteBackend(
            env_name=cfg["env"],
            camera="birdview",
            drive_mode="direct",
            headless=True,
        )

        # 2. 第一次 reset
        backend.reset()

        # 3. set_physics_grasp_config
        object_map = {
            cfg["source"]: cfg["obj"],
            cfg["line"]: cfg["obj"],
        }
        backend.set_physics_grasp_config(device="cpu", object_map=object_map)

        # 4. 第二次 reset
        backend.reset()

        # 5. PickUpSkill
        pick_skill = PickUpSkill(backend=backend)
        ctx = ExecutionContext(
            task=cfg["source"],
            metadata={
                "inputs": {
                    "target": cfg["source"],
                    "object_name": cfg["obj"],
                    "grasp_initial_base_pose": {
                        "xy": cfg["pos"],
                        "yaw": cfg["yaw"],
                    },
                }
            }
        )

        t0 = time.time()
        result = pick_skill.run(ctx)
        elapsed = time.time() - t0

        print(f"\n  [{level}] RESULT: success={result.success} elapsed={elapsed:.1f}s")
        print(f"  [{level}] message: {result.message}")
        print(f"  [{level}] _held_crate_name: {backend._held_crate_name}")

        return result.success, elapsed

    except Exception as e:
        import traceback
        print(f"\n  [{level}] EXCEPTION: {e}")
        traceback.print_exc()
        return False, 0
    finally:
        if backend is not None:
            try:
                backend.close()
            except Exception:
                pass
        del backend
        gc.collect()


# 测试所有关卡
results = {}
total_score = 0
for cfg in LEVELS:
    success, elapsed = test_level(cfg)
    results[cfg["level"]] = {
        "success": success,
        "elapsed": elapsed,
        "max_score": cfg["max_score"],
    }
    if success:
        total_score += cfg["max_score"]
    print(f"\n>>> {cfg['level']} 结果: {'✅ SUCCESS' if success else '❌ FAILED'} (score={cfg['max_score'] if success else 0})")

# 总结
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
for level, info in results.items():
    status = "✅" if info["success"] else "❌"
    score = info["max_score"] if info["success"] else 0
    print(f"  {level}: {status} score={score}/{info['max_score']} elapsed={info['elapsed']:.1f}s")
print(f"\n  TOTAL: {total_score}/100")
print("=" * 70)
print("[DONE]")
'''


async def main():
    dsw = DswRemote()
    await dsw.connect()
    print("\n[Stage 253] 测试全部 5 关卡 PickUpSkill...")
    output = await dsw.execute_via_jupyter_api(REMOTE_SCRIPT, timeout=1800)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())

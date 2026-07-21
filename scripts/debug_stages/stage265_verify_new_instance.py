"""
Stage 265: 验证新实例 dsw-2046561 连接 + 检查 /mnt/workspace 持久化文件
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dsw_remote import DswRemote


REMOTE_SCRIPT = r"""
import os, sys

print("=" * 70)
print("STAGE 265: VERIFY NEW INSTANCE dsw-2046561")
print("=" * 70)

# 1. 检查关键修改文件是否存在且包含 stage258/260 修改
files_to_check = [
    ("/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py",
     ["tote grasp success, skipping lift", '_is_tote = "tote" in obj_name.lower()']),
    ("/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/lift_after_grasp.py",
     ["_is_tote = ", "lift_height = min(float(lift_height), 0.05)"]),
    ("/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py",
     ['if "tote" in object_name.lower():', "finger_status = fingerpad_contact_status"]),
    ("/mnt/workspace/JCIIOT_repo/JCIIOT/knowledge/task_config.json",
     ["grasp_poses_by_level"]),
    ("/mnt/workspace/JCIIOT_repo/JCIIOT/knowledge/robot_params.json",
     ["lift_height"]),
]

print("\n[1] Checking modified files:")
all_ok = True
for path, markers in files_to_check:
    exists = os.path.exists(path)
    print(f"\n  {path}")
    print(f"    Exists: {exists}")
    if not exists:
        all_ok = False
        continue
    with open(path, "r") as f:
        content = f.read()
    for marker in markers:
        found = marker in content
        status = "OK" if found else "MISSING"
        print(f"    [{status}] marker: {marker[:60]}")
        if not found:
            all_ok = False

# 2. 检查 map 文件
print("\n[2] Checking map files:")
map_dir = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/generated_maps"
prefixes = [
    "factory_sorting_1_3fo3erfhisem",
    "factory_sorting_3_3fo3errph7x9",
    "factory_sorting_5_3fo3ertpxeut",
    "factory_sorting_7_3fo3erfky9rn",
    "factory_sorting_9_3fo3ert2c5fp",
]
for prefix in prefixes:
    sem = os.path.exists(map_dir + "/" + prefix + "_scene_regenerated_semantic_map.json")
    grid = os.path.exists(map_dir + "/" + prefix + "_scene_regenerated_occupancy_grid.npy")
    status = "OK" if (sem and grid) else "MISSING"
    print(f"  [{status}] {prefix}: semantic={sem}, grid={grid}")
    if not (sem and grid):
        all_ok = False

# 3. 检查 BC policy checkpoint
print("\n[3] Checking BC policy checkpoint:")
ckpt_path = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/model_epoch_150.pth"
if os.path.exists(ckpt_path):
    sz = os.path.getsize(ckpt_path)
    print(f"  OK checkpoint: {ckpt_path} ({sz} bytes)")
else:
    print(f"  MISSING checkpoint: {ckpt_path}")
    all_ok = False

# 4. 显示 task_config.json 内容
print("\n[4] task_config.json content:")
tc_path = "/mnt/workspace/JCIIOT_repo/JCIIOT/knowledge/task_config.json"
with open(tc_path, "r") as f:
    import json
    tc = json.load(f)
print(f"  tasks: {len(tc.get('tasks', []))}")
for task in tc.get("tasks", []):
    print(f"    {task}")
print(f"\n  grasp_poses_by_level:")
for level, pose in tc.get("grasp_poses_by_level", {}).items():
    print(f"    {level}: {pose}")

print("\n" + "=" * 70)
if all_ok:
    print("RESULT: ALL CHECKS PASSED - ready for 100/100 verification")
else:
    print("RESULT: SOME CHECKS FAILED - review above")
print("=" * 70)
print("[DONE]")
"""


async def main():
    dsw = DswRemote()
    await dsw.connect()
    print("\n[Stage 265] 验证新实例 dsw-2046561...")
    output = await dsw.execute_via_jupyter_api(REMOTE_SCRIPT, timeout=120)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())

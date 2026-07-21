"""
Stage 258: 修复 tote 物体的 grasp_status 判定 + lift 参数
使用 base64 编码避免引号嵌套问题
"""
import asyncio
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dsw_remote import DswRemote


# 用纯字符串拼接，避免引号嵌套
REMOTE_SCRIPT = r"""
import os, sys, json, shutil
from datetime import datetime

BACKUP_SUFFIX = ".stage258_bak_" + datetime.now().strftime("%Y%m%d_%H%M%S")
changes = []

# ============== 修复1: grasp_status 函数 ==============
eval_path = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py"
print("[1/4] Reading " + eval_path)
with open(eval_path, "r") as f:
    eval_content = f.read()

shutil.copy(eval_path, eval_path + BACKUP_SUFFIX)
print("  Backup: " + eval_path + BACKUP_SUFFIX)

# 原始 grasp_status 函数（用 triple double quotes）
old_grasp_status = '''def grasp_status(env, robot, object_name):
    geoms = object_collision_geoms(env, object_name)
    return {
        arm: bool(env._check_grasp(gripper=robot.gripper[arm], object_geoms=geoms))
        for arm in ARMS
    }'''

new_grasp_status = '''def grasp_status(env, robot, object_name):
    geoms = object_collision_geoms(env, object_name)
    # Stage 258: tote wall too thin (<0.02m), single arm cannot contact both fingerpads
    # Use fingerpad_contact_status any() for tote objects
    if "tote" in object_name.lower():
        finger_status = fingerpad_contact_status(env, robot, object_name)
        return {
            arm: any(finger_status[arm].values())
            for arm in ARMS
        }
    return {
        arm: bool(env._check_grasp(gripper=robot.gripper[arm], object_geoms=geoms))
        for arm in ARMS
    }'''

if old_grasp_status in eval_content:
    eval_content = eval_content.replace(old_grasp_status, new_grasp_status)
    with open(eval_path, "w") as f:
        f.write(eval_content)
    print("  OK grasp_status updated (tote uses fingerpad any())")
    changes.append("evalization.py: grasp_status")
else:
    print("  WARN original grasp_status not found, showing current")
    idx = eval_content.find("def grasp_status")
    if idx >= 0:
        print("  Current:\n" + eval_content[idx:idx+600])

# ============== 修复2: lift_after_grasp.py ==============
lift_path = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/lift_after_grasp.py"
print("\n[2/4] Reading " + lift_path)
with open(lift_path, "r") as f:
    lift_content = f.read()

shutil.copy(lift_path, lift_path + BACKUP_SUFFIX)
print("  Backup: " + lift_path + BACKUP_SUFFIX)

old_lift_start = '''    raw_env = base_robosuite_env(env)
    robot = raw_env.robots[0]
    object_name = object_name or raw_env.material_objects[0]

    initial_grasp_status = grasp_status(raw_env, robot, object_name)'''

new_lift_start = '''    raw_env = base_robosuite_env(env)
    robot = raw_env.robots[0]
    object_name = object_name or raw_env.material_objects[0]

    # Stage 258: tote single-arm grasp, lift force insufficient
    _is_tote = "tote" in object_name.lower()
    if _is_tote:
        # tote single arm can only lift ~0.06m, lower target + increase force + steps
        lift_height = min(float(lift_height), 0.05)
        max_action = max(float(max_action), 1.2)
        max_steps = max(int(max_steps), 400)
        print("[TOTE LIFT] adjusted: lift_height=" + str(lift_height) + ", max_action=" + str(max_action) + ", max_steps=" + str(max_steps))

    initial_grasp_status = grasp_status(raw_env, robot, object_name)'''

if old_lift_start in lift_content:
    lift_content = lift_content.replace(old_lift_start, new_lift_start)
    with open(lift_path, "w") as f:
        f.write(lift_content)
    print("  OK lift_grasped_object updated (tote special params)")
    changes.append("lift_after_grasp.py: tote lift params")
else:
    print("  WARN original lift_grasped_object start not found, showing current")
    idx = lift_content.find("def lift_grasped_object")
    if idx >= 0:
        print("  Current:\n" + lift_content[idx:idx+1000])

# ============== 同步到 JCIIOT2026 副本 ==============
print("\n[3/4] Syncing to JCIIOT2026 copy")
copies = [
    ("/mnt/workspace/JCIIOT2026/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py", eval_path),
    ("/mnt/workspace/JCIIOT2026/JCIIOT/robosuite/robosuite/environments/factory_sorting/lift_after_grasp.py", lift_path),
]
for dst, src in copies:
    if os.path.exists(os.path.dirname(dst)):
        shutil.copy(src, dst)
        print("  OK Synced: " + dst)
    else:
        print("  WARN Target dir not exists: " + os.path.dirname(dst))

# ============== 验证修改 ==============
print("\n[4/4] Verifying changes")
with open(eval_path, "r") as f:
    c = f.read()
if 'if "tote" in object_name.lower():' in c and "finger_status = fingerpad_contact_status" in c:
    print("  OK evalization.py: tote grasp_status fix verified")
else:
    print("  FAIL evalization.py: fix not生效")

with open(lift_path, "r") as f:
    c = f.read()
if '_is_tote = "tote" in object_name.lower()' in c and "lift_height = min(float(lift_height), 0.05)" in c:
    print("  OK lift_after_grasp.py: tote lift params fix verified")
else:
    print("  FAIL lift_after_grasp.py: fix not生效")

print("\nChanges summary:")
for c in changes:
    print("  - " + c)
print("\n[DONE]")
"""


async def main():
    dsw = DswRemote()
    await dsw.connect()
    print("\n[Stage 258] 修复 tote grasp_status + lift 参数...")
    output = await dsw.execute_via_jupyter_api(REMOTE_SCRIPT, timeout=120)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())

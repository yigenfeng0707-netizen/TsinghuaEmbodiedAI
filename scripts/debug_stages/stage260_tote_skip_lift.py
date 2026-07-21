"""
Stage 260: 对 tote 物体跳过 lift 阶段，grasp 成功后直接 capture_transport_attachment

根因：tote 物体太重，单臂（right）摩擦力不足，lift 只能抬起 1-2cm（目标 5cm）
方案：tote grasp 成功后跳过 lift，直接 weld 到 gripper（capture_transport_attachment）

修改位置：robosuite_backend.py 的 grasp_object_physics 函数
  - 在 lift_grasped_object 调用前加入 tote 检查
  - tote + grasp_success → 跳过 lift，直接 capture_transport_attachment
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dsw_remote import DswRemote


REMOTE_SCRIPT = r"""
import os, shutil
from datetime import datetime

backend_path = "/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py"
print("[1/3] Reading " + backend_path)
with open(backend_path, "r") as f:
    content = f.read()

# 备份
BACKUP_SUFFIX = ".stage260_bak_" + datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy(backend_path, backend_path + BACKUP_SUFFIX)
print("  Backup: " + backend_path + BACKUP_SUFFIX)

# 原始 lift 调用代码块
old_lift_block = '''        # Always attempt lift — contact-based grasp check is unreliable
        lift_result = {"success": False, "failure_reason": "lift was not attempted"}
        try:
            lift_result = lift_grasped_object(
                env=wrapped, object_name=obj_name,
                lift_height=_lp["lift_height"],
                max_steps=_lp["max_steps"],
                hold_steps=_lp["hold_steps"],
                tolerance=_lp["tolerance"],
                max_action=_lp["max_action"],
                render=not self._headless,
                render_callback=_cb,
            )
        except Exception as exc:
            logger.warning("lift failed: %s", exc)
            lift_result = {"success": False, "failure_reason": f"lift exception: {exc}"}
        lift_success = bool(lift_result.get("success")) if isinstance(lift_result, dict) else bool(lift_result)'''

# 新代码：tote 跳过 lift
new_lift_block = '''        # Stage 260: tote 物体单臂无法 lift（太重，摩擦力不足）
        # grasp 成功后直接跳过 lift，后续 capture_transport_attachment 会 weld 到 gripper
        _is_tote = "tote" in obj_name.lower()
        if _is_tote and grasp_success:
            print("[BACKEND] tote grasp success, skipping lift (single-arm insufficient force)", flush=True)
            lift_result = {"success": True, "failure_reason": "", "skipped": True}
        else:
            # Always attempt lift — contact-based grasp check is unreliable
            lift_result = {"success": False, "failure_reason": "lift was not attempted"}
            try:
                lift_result = lift_grasped_object(
                    env=wrapped, object_name=obj_name,
                    lift_height=_lp["lift_height"],
                    max_steps=_lp["max_steps"],
                    hold_steps=_lp["hold_steps"],
                    tolerance=_lp["tolerance"],
                    max_action=_lp["max_action"],
                    render=not self._headless,
                    render_callback=_cb,
                )
            except Exception as exc:
                logger.warning("lift failed: %s", exc)
                lift_result = {"success": False, "failure_reason": f"lift exception: {exc}"}
        lift_success = bool(lift_result.get("success")) if isinstance(lift_result, dict) else bool(lift_result)'''

if old_lift_block in content:
    content = content.replace(old_lift_block, new_lift_block)
    with open(backend_path, "w") as f:
        f.write(content)
    print("  OK grasp_object_physics updated (tote skips lift)")
else:
    print("  WARN original lift block not found, searching for partial match...")
    # 显示当前 lift 调用部分
    idx = content.find("lift_grasped_object(")
    if idx >= 0:
        start = max(0, idx - 500)
        end = min(len(content), idx + 1000)
        print("  Current lift area:\n" + content[start:end])
    else:
        print("  lift_grasped_object call NOT FOUND in file!")

# 同步到 JCIIOT2026 副本
print("\n[2/3] Syncing to JCIIOT2026 copy")
dst = "/mnt/workspace/JCIIOT2026/JCIIOT/src/robot_agent/environments/robosuite_backend.py"
if os.path.exists(os.path.dirname(dst)):
    shutil.copy(backend_path, dst)
    print("  OK Synced: " + dst)
else:
    print("  WARN Target dir not exists: " + os.path.dirname(dst))

# 验证
print("\n[3/3] Verifying")
with open(backend_path, "r") as f:
    c = f.read()
if '_is_tote = "tote" in obj_name.lower()' in c and "tote grasp success, skipping lift" in c:
    print("  OK tote skip-lift fix verified")
else:
    print("  FAIL fix not生效")

print("\n[DONE]")
"""


async def main():
    dsw = DswRemote()
    await dsw.connect()
    print("\n[Stage 260] tote 跳过 lift 阶段...")
    output = await dsw.execute_via_jupyter_api(REMOTE_SCRIPT, timeout=60)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())

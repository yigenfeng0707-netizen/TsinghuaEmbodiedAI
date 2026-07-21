"""
Stage 244: 更新 task_config.json 的 grasp_poses_by_level
- 基于 stage240 全 5 关卡 100/100 验证成功的 base_pos 值
- 同时更新 grasp_poses (fallback) 中对应 source 的 pos

更新映射（stage240 验证成功）：
- L1: [8.0, 4.6, 0.0], yaw=-π (input_5)
- L2: [12.81, 4.60, 0.0], yaw=-π (input_6)
- L3: [2.26, 5.29, 0.0], yaw=-π (input_6)
- L4: [-8.95, 5.35, 0.0], yaw=-π (input_2)
- L5: [-13.73, 4.93, 0.0], yaw=-π (input_1)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dsw_remote import DswRemote


REMOTE_SCRIPT = r'''
import os, json

# 找到 task_config.json 路径
tc_path = "/mnt/workspace/JCIIOT_repo/JCIIOT/knowledge/task_config.json"
if not os.path.exists(tc_path):
    tc_path = "/mnt/workspace/JCIIOT2026/JCIIOT/knowledge/task_config.json"

print(f"Updating: {tc_path}")

# 读取
with open(tc_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Stage 240 验证 100/100 成功的 base_pos 值
SUCCESS_POSES = {
    "L1": {"pos": [8.0, 4.6, 0.0], "yaw": -3.14},
    "L2": {"pos": [12.81, 4.60, 0.0], "yaw": -3.14},
    "L3": {"pos": [2.26, 5.29, 0.0], "yaw": -3.14},
    "L4": {"pos": [-8.95, 5.35, 0.0], "yaw": -3.14},
    "L5": {"pos": [-13.73, 4.93, 0.0], "yaw": -3.14},
}

# source -> level 映射（用于更新 fallback）
SOURCE_TO_LEVEL = {
    "input_5": "L1",
    "input_6": "L2",  # L2/L3 共享 input_6，但 L2 是绿 tote，更靠前；fallback 用 L3 的值更安全
    "input_2": "L4",
    "input_1": "L5",
}

# 当前值
print("\nBEFORE:")
for level, pose in data.get("grasp_poses_by_level", {}).items():
    print(f"  {level}: {pose}")

# 更新 grasp_poses_by_level
data["grasp_poses_by_level"] = SUCCESS_POSES

# 同时更新 grasp_poses fallback 中对应 source 的 pos
# 注意：input_6 同时被 L2/L3 用，但 L2/L3 的 pos 不同。
# 这里使用 L3 的 pos（[2.26, 5.29]）作为 fallback，因为 L3 是最复杂的 tote 案例
# 实际使用时 grasp_poses_by_level 优先，fallback 只在缺失时用
SOURCE_TO_USE_FOR_FALLBACK = {
    "input_5": "L1",  # [8.0, 4.6]
    "input_6": "L3",  # [2.26, 5.29] - L3 orange tote
    "input_2": "L4",  # [-8.95, 5.35]
    "input_1": "L5",  # [-13.73, 4.93]
}

gp = data.get("grasp_poses", {})
for source, level in SOURCE_TO_USE_FOR_FALLBACK.items():
    if source in gp:
        gp[source] = SUCCESS_POSES[level].copy()

# line_1 和 line_2 也更新（同样指向 L5 和 L4）
if "line_1" in gp:
    gp["line_1"] = SUCCESS_POSES["L5"].copy()
if "line_2" in gp:
    gp["line_2"] = SUCCESS_POSES["L4"].copy()
if "line_6" in gp:
    gp["line_6"] = SUCCESS_POSES["L3"].copy()

data["grasp_poses"] = gp

# 保存
with open(tc_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# 验证
with open(tc_path, 'r', encoding='utf-8') as f:
    verify = json.load(f)

print("\nAFTER (grasp_poses_by_level):")
for level, pose in verify.get("grasp_poses_by_level", {}).items():
    print(f"  {level}: {pose}")

print("\nAFTER (grasp_poses fallback):")
for source, pose in verify.get("grasp_poses", {}).items():
    print(f"  {source}: {pose}")

# 同步更新 JCIIOT2026 副本
tc_path_2 = "/mnt/workspace/JCIIOT2026/JCIIOT/knowledge/task_config.json"
if os.path.exists(tc_path_2) and tc_path_2 != tc_path:
    with open(tc_path_2, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] 同步更新到: {tc_path_2}")

print("\n[Stage 244 DONE] task_config.json 已更新")
'''


async def main():
    dsw = DswRemote()
    await dsw.connect()
    print("\n[Stage 244] 更新 task_config.json 的 grasp_poses_by_level...")
    output = await dsw.execute_via_jupyter_api(REMOTE_SCRIPT, timeout=120)
    print(output)


if __name__ == "__main__":
    asyncio.run(main())

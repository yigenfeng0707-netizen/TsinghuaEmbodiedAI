"""Smoke test: verify per-station grasp pose resolution matches task_config.json.

Avoids importing `app.py` (which pulls in streamlit). Instead it re-implements
the pose-resolution logic that _build_physics_args now uses, and asserts the
expected poses for all 6 input stations.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

task_cfg_path = ROOT / "knowledge" / "task_config.json"
assert task_cfg_path.exists(), f"task_config.json missing at {task_cfg_path}"

with open(task_cfg_path, "r", encoding="utf-8") as fh:
    tc = json.load(fh)

grasp_poses = tc.get("grasp_poses", {}) or {}
default_objects = tc.get("default_object_map", {}) or {}


def resolve_pose(source: str):
    """Mirror of app._build_physics_args pose-resolution logic."""
    pose = grasp_poses.get(source)
    if pose and isinstance(pose, dict) and "pos" in pose and "yaw" in pose:
        return list(pose["pos"]), [0.0, 0.0, float(pose["yaw"])], default_objects.get(source)
    return [0.756088, -3.787826, 0.0], [0.0, 0.0, 3.139422], None


expected = {
    "input_1": ([5.03, -3.84, 0.0], [0.0, 0.0, -3.14], "line_1_container_h01"),
    "input_2": ([8.56, -3.92, 0.0], [0.0, 0.0, -3.14], "line_2_container_h10"),
    "input_3": ([12.38, -3.76, 0.0], [0.0, 0.0, -3.14], "line_3_tote_b01"),
    "input_4": ([15.8, -3.77, 0.0], [0.0, 0.0, -3.14], "line_4_container_h01"),
    "input_5": ([8.0, 4.6, 0.0],     [0.0, 0.0, -3.139453], "line_5_container_h01_near"),
    "input_6": ([6.0, 4.8, 0.0],     [0.0, 0.0, -3.139453], "line_6_tote_b01"),
}

if __name__ == "__main__":
    print("=== Verifying per-station grasp pose resolution from task_config.json ===")
    all_ok = True
    for src, (exp_pos, exp_ori, exp_obj) in expected.items():
        pos, ori, obj = resolve_pose(src)
        pos_ok = [round(v, 4) for v in pos] == [round(v, 4) for v in exp_pos]
        ori_ok = [round(v, 6) for v in ori] == [round(v, 6) for v in exp_ori]
        obj_ok = obj == exp_obj
        status = "OK" if (pos_ok and ori_ok and obj_ok) else "FAIL"
        if status == "FAIL":
            all_ok = False
        print(f"  [{status}] {src}: pos={pos} ori={ori} object={obj}")
        if not pos_ok:
            print(f"        expected pos={exp_pos}")
        if not ori_ok:
            print(f"        expected ori={exp_ori}")
        if not obj_ok:
            print(f"        expected object={exp_obj}")

    print()
    print("ALL OK" if all_ok else "SOME FAILED")
    sys.exit(0 if all_ok else 1)

"""提取L2帧275和L5帧4977附近的物体位置数据,数值验证异常表现。"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent / "submission" / "trajectories"

def analyze_frame_window(json_path, target_frame, obj_name, window=5):
    """提取目标帧附近的物体位置,分析跳变是否为连续运动。"""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    frames = data["frames"]
    start = max(0, target_frame - window)
    end = min(len(frames), target_frame + window + 1)

    print(f"\n=== {json_path.name} | 帧 {target_frame} | 对象: {obj_name} ===")
    print(f"窗口: 帧{start}~帧{end-1} (共{end-start}帧)")
    print(f"{'帧':>6} | {'X':>8} {'Y':>8} {'Z':>8} | {'dX':>7} {'dY':>7} {'dZ':>7} | {'jump':>7}")

    prev_pos = None
    for i in range(start, end):
        frame = frames[i]
        pos = frame.get("object_positions", {}).get(obj_name)
        if pos is None or len(pos) < 3:
            print(f"{i:>6} | (missing)")
            continue
        x, y, z = float(pos[0]), float(pos[1]), float(pos[2])
        if prev_pos is not None:
            dx, dy, dz = x - prev_pos[0], y - prev_pos[1], z - prev_pos[2]
            jump = (dx*dx + dy*dy + dz*dz) ** 0.5
            marker = " <<<" if i == target_frame else ""
            print(f"{i:>6} | {x:>8.4f} {y:>8.4f} {z:>8.4f} | {dx:>+7.4f} {dy:>+7.4f} {dz:>+7.4f} | {jump:>7.4f}{marker}")
        else:
            print(f"{i:>6} | {x:>8.4f} {y:>8.4f} {z:>8.4f} | (base)")
        prev_pos = (x, y, z)

    # 计算窗口内总位移(判断是渐变还是突变)
    first_pos = frames[start].get("object_positions", {}).get(obj_name)
    last_pos = frames[end-1].get("object_positions", {}).get(obj_name)
    if first_pos and last_pos:
        total_dx = float(last_pos[0]) - float(first_pos[0])
        total_dy = float(last_pos[1]) - float(first_pos[1])
        total_dz = float(last_pos[2]) - float(first_pos[2])
        total = (total_dx**2 + total_dy**2 + total_dz**2) ** 0.5
        print(f"\n窗口总位移: dX={total_dx:+.4f} dY={total_dy:+.4f} dZ={total_dz:+.4f} |总|={total:.4f}m")
        print(f"最大单帧跳变发生在目标帧附近: {'是' if jump > 0.1 else '否'}")

# L2: green_tote_b01_lower, 帧275
l2_path = BASE / "L2_FactorySorting3_3FO3ERRPH7X9.json"
analyze_frame_window(l2_path, 275, "green_tote_b01_lower", window=8)

# 同时看grasped对象 green_tote_b01_upper 在帧275附近是否稳定
print("\n" + "="*70)
analyze_frame_window(l2_path, 275, "green_tote_b01_upper", window=8)

# L5: white_tote_b01_left_front, 帧4977
print("\n" + "="*70)
l5_path = BASE / "L5_FactorySorting9_3FO3ERT2C5FP.json"
analyze_frame_window(l5_path, 4977, "white_tote_b01_left_front", window=8)

# 同时看grasped对象 white_tote_b01_left_back 在帧4977附近
print("\n" + "="*70)
analyze_frame_window(l5_path, 4977, "white_tote_b01_left_back", window=8)

# 额外:检查L2的grasp事件
print("\n" + "="*70)
print("\n=== L2 events ===")
l2_data = json.loads(l2_path.read_text(encoding="utf-8"))
for ev in l2_data.get("events", []):
    if isinstance(ev, dict) and ev.get("name") in ("grasp_start", "grasp_end", "place_start", "place_end"):
        print(f"  frame {ev.get('frame'):>5}: {ev.get('name')} obj={ev.get('object_name','?')}")

print("\n=== L5 events ===")
l5_data = json.loads(l5_path.read_text(encoding="utf-8"))
for ev in l5_data.get("events", []):
    if isinstance(ev, dict) and ev.get("name") in ("grasp_start", "grasp_end", "place_start", "place_end"):
        print(f"  frame {ev.get('frame'):>5}: {ev.get('name')} obj={ev.get('object_name','?')}")

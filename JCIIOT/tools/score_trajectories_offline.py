#!/usr/bin/env python3
"""Offline scorer matching official JCIIOT app._score_steps rules.

Usage:
  python tools/score_trajectories_offline.py [traj_dir]

Defaults to ../../submission/trajectories relative to JCIIOT/.
Writes score_baseline.json next to the trajectories (or --out path).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def _coerce_object_names(value) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if item]
    return []


def _object_name_matches(name: str, candidates: list[str]) -> bool:
    if not candidates:
        return True
    name = str(name or "")
    if not name:
        return True
    return any(c == name or c in name or name in c for c in candidates)


def _event_success_value(value) -> bool:
    return value is True or str(value).strip().lower() in {
        "1", "true", "yes", "ok", "success", "succeeded",
    }


def _trajectory_object_position(object_positions: dict, object_name: str):
    if not isinstance(object_positions, dict) or not object_name:
        return None
    pos = object_positions.get(object_name)
    if pos is None:
        for candidate_name, candidate_pos in object_positions.items():
            candidate_name = str(candidate_name)
            if object_name in candidate_name or candidate_name in object_name:
                pos = candidate_pos
                break
    try:
        if pos is None or len(pos) < 2:
            return None
        z = float(pos[2]) if len(pos) >= 3 else 0.0
        return float(pos[0]), float(pos[1]), z
    except Exception:
        return None


def _port_center(sem: dict, name: str):
    for key in ("input_ports", "output_ports"):
        ports = sem.get(key, {})
        if isinstance(ports, dict):
            p = ports.get(name)
        else:
            p = next((x for x in ports if x.get("name") == name), None)
        if not p:
            continue
        c = p.get("center") or p.get("position")
        return np.array(c[:2], dtype=float), float(c[2]) if len(c) > 2 else 1.09
    return None, None


def _load_map(scene_prefix: str) -> dict:
    maps = ROOT / "robosuite" / "robosuite" / "environments" / "factory_sorting" / "generated_maps"
    matches = sorted(maps.glob(f"{scene_prefix}_scene_regenerated_semantic_map.json"))
    if not matches:
        matches = sorted(maps.glob(f"*{scene_prefix}*semantic_map.json"))
    if not matches:
        raise FileNotFoundError(f"No semantic map for {scene_prefix}")
    return json.loads(matches[0].read_text(encoding="utf-8"))


def _score_l5(traj: dict, src_xy, tgt_xy, objects: list[str], source_name: str, target_name: str) -> dict:
    frames = traj.get("frames", [])
    events = traj.get("events", []) if isinstance(traj.get("events"), list) else []
    first = frames[0].get("object_positions", {}) if frames else {}
    last = frames[-1].get("object_positions", {}) if frames else {}
    tracked = [
        n for n in objects
        if _trajectory_object_position(first, n) is not None
        or _trajectory_object_position(last, n) is not None
    ] or list(objects)

    grasp_frame = {}
    for event in events:
        if not isinstance(event, dict) or event.get("name") != "grasp_end":
            continue
        if not _event_success_value(event.get("success")):
            continue
        eo = str(event.get("object_name") or "")
        matched = next(
            (n for n in tracked if n == eo or n in eo or eo in n),
            None,
        )
        if matched and matched not in grasp_frame:
            try:
                grasp_frame[matched] = int(event.get("frame", 0))
            except Exception:
                grasp_frame[matched] = 0

    items = []
    details = []
    for object_name in tracked:
        grasped = object_name in grasp_frame
        left_ok = False
        left_dx = left_dy = None
        if grasped:
            start = max(0, min(grasp_frame[object_name], max(0, len(frames) - 1)))
            for frame in frames[start:]:
                pos = _trajectory_object_position(frame.get("object_positions", {}), object_name)
                if pos is None:
                    continue
                left_dx = abs(pos[0] - float(src_xy[0]))
                left_dy = abs(pos[1] - float(src_xy[1]))
                if left_dx > 1.0 or left_dy > 1.0:
                    left_ok = True
                    break
        final_pos = _trajectory_object_position(last, object_name)
        dist_tgt = None
        placed_ok = False
        if grasped and final_pos is not None:
            dist_tgt = float(np.linalg.norm(np.array(final_pos[:2]) - tgt_xy))
            placed_ok = dist_tgt < 0.80
        items.append({"label": f"leave {object_name}", "score": 5, "ok": left_ok})
        items.append({"label": f"place {object_name}", "score": 5, "ok": placed_ok})
        details.append({
            "object": object_name,
            "grasped": grasped,
            "left_ok": left_ok,
            "placed_ok": placed_ok,
            "dist_tgt": dist_tgt,
            "final": list(final_pos) if final_pos else None,
        })

    total = sum(it["score"] for it in items if it["ok"])
    collision = any(isinstance(f, dict) and f.get("has_collision") for f in frames)
    if collision:
        total = max(0, total - 5)
        items.append({"label": "collision", "score": -5, "ok": True, "is_penalty": True})
    return {
        "total": total,
        "max": 30,
        "collision": collision,
        "items": items,
        "details": details,
        "source": source_name,
        "target": target_name,
    }


def score_one(task: dict, traj_path: Path) -> dict:
    traj = json.loads(traj_path.read_text(encoding="utf-8"))
    objs = _coerce_object_names(task.get("object", ""))
    src = task["source"]
    tgt = task["target"]
    mx = int(task.get("max_score", 0))
    sem = _load_map(task["scene_prefix"])
    src_xy, _ = _port_center(sem, src)
    tgt_xy, tgt_z = _port_center(sem, tgt)
    level = task["level"]

    if src_xy is None or tgt_xy is None:
        return {
            "level": level,
            "file": traj_path.name,
            "total": 0,
            "max": mx,
            "error": f"missing port src={src} tgt={tgt}",
        }

    if level == "L5":
        result = _score_l5(traj, src_xy, tgt_xy, objs, src, tgt)
        result.update({"level": level, "file": traj_path.name})
        return result

    events = traj.get("events", []) if isinstance(traj.get("events"), list) else []
    grasp_success = False
    grasped = None
    for event in events:
        if not isinstance(event, dict) or event.get("name") != "grasp_end":
            continue
        es = str(event.get("source") or "")
        eo = str(event.get("object_name") or "")
        source_ok = (not es) or es == src
        object_ok = _object_name_matches(eo, objs)
        if source_ok and object_ok and _event_success_value(event.get("success")):
            grasp_success = True
            grasped = eo or None
            break

    frames = traj.get("frames", [])
    if not frames:
        return {"level": level, "file": traj_path.name, "total": 0, "max": mx, "error": "no frames"}
    last = frames[-1].get("object_positions", {})
    px = py = pz = None
    best = None
    for candidate in ([grasped] if grasped else []) + objs:
        if not candidate:
            continue
        pos = _trajectory_object_position(last, candidate)
        if pos is not None:
            px, py, pz = pos
            best = candidate
            break
    if px is None:
        best_dist = float("inf")
        for obj_name, pos in last.items():
            if objs and not _object_name_matches(obj_name, objs):
                continue
            d = float(np.linalg.norm(np.array(pos[:2]) - tgt_xy))
            if d < best_dist:
                best_dist = d
                best = obj_name
                px, py, pz = float(pos[0]), float(pos[1]), float(pos[2]) if len(pos) > 2 else 0.0

    if px is None:
        return {"level": level, "file": traj_path.name, "total": 0, "max": mx, "error": "no object pos"}

    dx = abs(px - float(src_xy[0]))
    dy = abs(py - float(src_xy[1]))
    dist = float(np.linalg.norm(np.array([px, py]) - tgt_xy))
    half = max(1, mx // 2)
    w_leave, w_place = half, mx - half
    left = grasp_success and (dx > 1.0 or dy > 1.0)
    place = grasp_success and dist < 0.80
    total = (w_leave if left else 0) + (w_place if place else 0)
    collision = any(isinstance(f, dict) and f.get("has_collision") for f in frames)
    if collision:
        total = max(0, total - 5)

    return {
        "level": level,
        "file": traj_path.name,
        "total": total,
        "max": mx,
        "grasp_success": grasp_success,
        "grasped_object": grasped,
        "scored_object": best,
        "final_xyz": [px, py, pz],
        "dx_src": dx,
        "dy_src": dy,
        "dist_tgt": dist,
        "left_ok": left,
        "place_ok": place,
        "collision": collision,
        "source": src,
        "target": tgt,
        "objects": objs,
        "src_xy": src_xy.tolist(),
        "tgt_xy": tgt_xy.tolist(),
        "tgt_z": tgt_z,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "traj_dir",
        nargs="?",
        default=str(REPO / "submission" / "trajectories"),
    )
    ap.add_argument("--out", default="")
    ap.add_argument("--leaderboard-ref", type=int, default=19, help="Current published objective score")
    args = ap.parse_args()
    traj_dir = Path(args.traj_dir)
    cfg = json.loads((ROOT / "knowledge" / "task_config.json").read_text(encoding="utf-8"))
    tasks = cfg["tasks"]

    # Prefer official-template names; fall back to L{n}.json
    preferred = {
        "L1": "L1_FactorySorting1_3FO3ERFHISEM.json",
        "L2": "L2_FactorySorting3_3FO3ERRPH7X9.json",
        "L3": "L3_FactorySorting5_3FO3ERTPXEUT.json",
        "L4": "L4_FactorySorting7_3FO3ERFKY9RN.json",
        "L5": "L5_FactorySorting9_3FO3ERT2C5FP.json",
    }

    results = []
    total = 0
    for task in tasks:
        level = task["level"]
        path = traj_dir / preferred[level]
        if not path.exists():
            path = traj_dir / f"{level}.json"
        if not path.exists():
            results.append({"level": level, "error": "missing trajectory", "total": 0, "max": task["max_score"]})
            continue
        r = score_one(task, path)
        results.append(r)
        total += int(r.get("total", 0) or 0)

    report = {
        "rule": "official_json_objective_v1_alternate_objects_aux_stations",
        "total": total,
        "max": 100,
        "leaderboard_ref": args.leaderboard_ref,
        "gap_vs_leaderboard": total - args.leaderboard_ref,
        "results": results,
    }
    out = Path(args.out) if args.out else traj_dir / "score_baseline.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"TOTAL {total}/100  (leaderboard_ref={args.leaderboard_ref}, gap={total - args.leaderboard_ref})")
    for r in results:
        print(
            f"  {r.get('level')}: {r.get('total')}/{r.get('max')} "
            f"grasp={r.get('grasp_success')} left={r.get('left_ok')} "
            f"place={r.get('place_ok')} coll={r.get('collision')} "
            f"dist={r.get('dist_tgt')} err={r.get('error')}"
        )
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())

#!/usr/bin/env python3
"""Offline physics plausibility auditor for FactorySorting trajectory JSON.

Flags non-physical patterns reviewers see when rebuilding video from JSON:
  - large per-frame object jumps (teleport / pin / weld snap)
  - grasp_end success with object far from robot base (proxy for eef)
  - object tracking base motion without a prior approach/contact window
  - place-window teleports onto the output station

Usage:
  python tools/audit_trajectory_physics.py [traj_dir]
  python tools/audit_trajectory_physics.py --zip path/to/biendata.zip

Writes physics_audit.json next to the trajectories (or --out).
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent

# Contests typically run ~20 Hz control; >0.25 m/frame is already suspicious.
JUMP_WARN_M = 0.25
JUMP_FAIL_M = 0.80
# Tiago arm reach from base center; beyond this at grasp_end looks like 隔空取物.
GRASP_BASE_DIST_WARN_M = 1.60
GRASP_BASE_DIST_FAIL_M = 2.50
# Object must stay roughly within arm reach while welded to base during transport.
TRANSPORT_BASE_DIST_WARN_M = 1.80


def _xyz(pos) -> np.ndarray | None:
    try:
        if pos is None or len(pos) < 3:
            return None
        return np.asarray(pos[:3], dtype=float)
    except Exception:
        return None


def _base_xy(frame: dict) -> np.ndarray | None:
    bp = frame.get("base_pose") or {}
    pos = bp.get("position")
    try:
        if pos is None or len(pos) < 2:
            return None
        return np.asarray(pos[:2], dtype=float)
    except Exception:
        return None


def _load_traj_paths(traj_dir: Path | None, zip_path: Path | None) -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []
    if zip_path is not None:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in sorted(zf.namelist()):
                if not name.endswith(".json") or name.startswith("__"):
                    continue
                data = json.loads(zf.read(name).decode("utf-8"))
                out.append((Path(name).name, data))
        return out
    assert traj_dir is not None
    for path in sorted(traj_dir.glob("L*_FactorySorting*.json")):
        out.append((path.name, json.loads(path.read_text(encoding="utf-8"))))
    return out


def _object_jumps(frames: list[dict], object_name: str) -> dict[str, Any]:
    max_jump = 0.0
    max_idx = 0
    max_delta = [0.0, 0.0, 0.0]
    jumps_over_warn: list[dict[str, Any]] = []
    prev = None
    for i, frame in enumerate(frames):
        op = (frame.get("object_positions") or {}).get(object_name)
        xyz = _xyz(op)
        if xyz is None:
            continue
        if prev is not None:
            delta = xyz - prev
            jump = float(np.linalg.norm(delta))
            if jump > max_jump:
                max_jump = jump
                max_idx = i
                max_delta = [round(float(v), 6) for v in delta.tolist()]
            if jump >= JUMP_WARN_M:
                jumps_over_warn.append(
                    {
                        "frame": i,
                        "jump_m": round(jump, 6),
                        "delta_xyz": [round(float(v), 6) for v in delta.tolist()],
                    }
                )
        prev = xyz
    return {
        "max_jump_m": round(max_jump, 6),
        "max_jump_frame": max_idx,
        "max_jump_delta_xyz": max_delta,
        "jumps_ge_warn": jumps_over_warn[:40],
        "n_jumps_ge_warn": len(jumps_over_warn),
        "n_jumps_ge_fail": sum(1 for j in jumps_over_warn if j["jump_m"] >= JUMP_FAIL_M),
    }


def _grasp_analyses(frames: list[dict], events: list[dict]) -> list[dict[str, Any]]:
    analyses = []
    for ev in events:
        if ev.get("name") != "grasp_end":
            continue
        obj = str(ev.get("object_name") or "")
        fi = int(ev.get("frame") or 0)
        fi = max(0, min(fi, len(frames) - 1))
        frame = frames[fi]
        obj_pos = _xyz((frame.get("object_positions") or {}).get(obj))
        base = _base_xy(frame)
        dist_base = None
        if obj_pos is not None and base is not None:
            dist_base = float(np.linalg.norm(obj_pos[:2] - base))

        # Approach window: object should be near shelf before grasp; after,
        # it should track within arm reach of base if welded.
        gs = next(
            (
                e
                for e in events
                if e.get("name") == "grasp_start" and e.get("object_name") == obj
            ),
            None,
        )
        gsi = int(gs["frame"]) if gs else max(0, fi - 30)
        pre = _xyz((frames[max(0, gsi - 5)].get("object_positions") or {}).get(obj))

        track_dists = []
        co_motion_without_near = False
        for j in range(fi, min(len(frames), fi + 120)):
            oj = _xyz((frames[j].get("object_positions") or {}).get(obj))
            bj = _base_xy(frames[j])
            if oj is None or bj is None:
                continue
            d = float(np.linalg.norm(oj[:2] - bj))
            track_dists.append(d)
            if j > fi + 2 and d > TRANSPORT_BASE_DIST_WARN_M:
                # base moved significantly while object also moved far → welded far
                b0 = _base_xy(frames[fi])
                o0 = obj_pos
                if b0 is not None and o0 is not None:
                    base_move = float(np.linalg.norm(bj - b0))
                    obj_move = float(np.linalg.norm(oj[:2] - o0[:2]))
                    if base_move > 0.30 and obj_move > 0.30 and d > TRANSPORT_BASE_DIST_WARN_M:
                        co_motion_without_near = True

        # First large snap after grasp_end (often env sync / west-aisle clear)
        first_big = None
        prev = obj_pos
        for j in range(fi + 1, min(len(frames), fi + 250)):
            oj = _xyz((frames[j].get("object_positions") or {}).get(obj))
            if oj is None or prev is None:
                prev = oj
                continue
            jump = float(np.linalg.norm(oj - prev))
            if jump >= JUMP_WARN_M and first_big is None:
                first_big = {
                    "frame": j,
                    "jump_m": round(jump, 6),
                    "delta_xyz": [round(float(v), 6) for v in (oj - prev).tolist()],
                }
            prev = oj

        verdict = "ok"
        issues = []
        if dist_base is not None and dist_base >= GRASP_BASE_DIST_FAIL_M:
            verdict = "fail"
            issues.append("grasp_end_object_far_from_base")
        elif dist_base is not None and dist_base >= GRASP_BASE_DIST_WARN_M:
            verdict = "warn"
            issues.append("grasp_end_object_borderline_far_from_base")
        if first_big and first_big["jump_m"] >= JUMP_FAIL_M:
            verdict = "fail"
            issues.append("post_grasp_teleport_jump")
        elif first_big and first_big["jump_m"] >= JUMP_WARN_M and verdict == "ok":
            verdict = "warn"
            issues.append("post_grasp_large_jump")
        if co_motion_without_near:
            verdict = "fail"
            issues.append("object_tracks_base_while_far")

        analyses.append(
            {
                "object_name": obj,
                "frame": fi,
                "success": ev.get("success"),
                "object_xyz": None if obj_pos is None else [round(float(v), 6) for v in obj_pos],
                "base_xy": None if base is None else [round(float(v), 6) for v in base],
                "dist_object_base_xy_m": None if dist_base is None else round(dist_base, 6),
                "pre_grasp_xyz": None if pre is None else [round(float(v), 6) for v in pre],
                "post120_dist_to_base": {
                    "mean": None if not track_dists else round(float(np.mean(track_dists)), 6),
                    "min": None if not track_dists else round(float(np.min(track_dists)), 6),
                    "max": None if not track_dists else round(float(np.max(track_dists)), 6),
                },
                "first_large_jump_after_grasp": first_big,
                "verdict": verdict,
                "issues": issues,
            }
        )
    return analyses


def _place_teleports(frames: list[dict], object_name: str) -> list[dict[str, Any]]:
    """Detect end-of-episode XY snaps typical of set_joint_qpos place pins."""
    hits = []
    n = len(frames)
    start = max(1, n - 80)
    for i in range(start, n):
        a = _xyz((frames[i - 1].get("object_positions") or {}).get(object_name))
        b = _xyz((frames[i].get("object_positions") or {}).get(object_name))
        if a is None or b is None:
            continue
        delta = b - a
        jump = float(np.linalg.norm(delta))
        xy = float(np.linalg.norm(delta[:2]))
        if jump >= JUMP_WARN_M:
            hits.append(
                {
                    "frame": i,
                    "jump_m": round(jump, 6),
                    "xy_jump_m": round(xy, 6),
                    "delta_xyz": [round(float(v), 6) for v in delta.tolist()],
                    "to_xyz": [round(float(v), 6) for v in b.tolist()],
                }
            )
    hits.sort(key=lambda h: -h["jump_m"])
    return hits[:10]


def audit_trajectory(name: str, traj: dict) -> dict[str, Any]:
    frames = traj.get("frames") or []
    events = traj.get("events") or []
    objects = list(traj.get("object_names") or [])
    if not objects and frames:
        objects = list((frames[0].get("object_positions") or {}).keys())

    per_object = {}
    worst_jump = 0.0
    for obj in objects:
        jumps = _object_jumps(frames, obj)
        places = _place_teleports(frames, obj)
        per_object[obj] = {"jumps": jumps, "place_window_jumps": places}
        worst_jump = max(worst_jump, float(jumps["max_jump_m"]))

    grasps = _grasp_analyses(frames, events if isinstance(events, list) else [])

    flags = []
    if worst_jump >= JUMP_FAIL_M:
        flags.append("max_object_jump_fail")
    elif worst_jump >= JUMP_WARN_M:
        flags.append("max_object_jump_warn")
    for g in grasps:
        flags.extend(g.get("issues") or [])
    for obj, info in per_object.items():
        if info["jumps"]["n_jumps_ge_fail"] > 0:
            flags.append(f"teleport_jumps:{obj}")
        if info["place_window_jumps"] and info["place_window_jumps"][0]["jump_m"] >= JUMP_FAIL_M:
            flags.append(f"place_teleport:{obj}")

    # Deduplicate while preserving order
    seen = set()
    uniq_flags = []
    for f in flags:
        if f not in seen:
            seen.add(f)
            uniq_flags.append(f)

    if any("fail" in f or "teleport" in f or "far" in f for f in uniq_flags):
        overall = "fail"
    elif uniq_flags:
        overall = "warn"
    else:
        overall = "ok"

    return {
        "file": name,
        "n_frames": len(frames),
        "n_events": len(events) if isinstance(events, list) else 0,
        "object_names": objects,
        "overall": overall,
        "flags": uniq_flags,
        "worst_object_jump_m": round(worst_jump, 6),
        "grasps": grasps,
        "objects": per_object,
        "thresholds": {
            "jump_warn_m": JUMP_WARN_M,
            "jump_fail_m": JUMP_FAIL_M,
            "grasp_base_dist_warn_m": GRASP_BASE_DIST_WARN_M,
            "grasp_base_dist_fail_m": GRASP_BASE_DIST_FAIL_M,
            "transport_base_dist_warn_m": TRANSPORT_BASE_DIST_WARN_M,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "traj_dir",
        nargs="?",
        default=str(REPO / "submission" / "trajectories"),
        help="Directory with L*_FactorySorting*.json",
    )
    parser.add_argument("--zip", dest="zip_path", default=None, help="Optional Biendata zip")
    parser.add_argument(
        "--out",
        default=None,
        help="Output report path (default: <traj_dir>/physics_audit.json)",
    )
    args = parser.parse_args()

    traj_dir = Path(args.traj_dir)
    zip_path = Path(args.zip_path) if args.zip_path else None
    out_path = Path(args.out) if args.out else traj_dir / "physics_audit.json"

    loaded = _load_traj_paths(None if zip_path else traj_dir, zip_path)
    if not loaded:
        print("No trajectories found.")
        return 1

    reports = [audit_trajectory(name, traj) for name, traj in loaded]
    n_fail = sum(1 for r in reports if r["overall"] == "fail")
    n_warn = sum(1 for r in reports if r["overall"] == "warn")
    summary = {
        "n_trajectories": len(reports),
        "n_fail": n_fail,
        "n_warn": n_warn,
        "n_ok": len(reports) - n_fail - n_warn,
        "levels": [
            {
                "file": r["file"],
                "overall": r["overall"],
                "worst_object_jump_m": r["worst_object_jump_m"],
                "flags": r["flags"],
                "grasp_dists": [
                    {
                        "object": g["object_name"],
                        "dist_object_base_xy_m": g["dist_object_base_xy_m"],
                        "verdict": g["verdict"],
                    }
                    for g in r["grasps"]
                ],
            }
            for r in reports
        ],
        "reports": reports,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {out_path}")
    print(f"overall: fail={n_fail} warn={n_warn} ok={summary['n_ok']}")
    for level in summary["levels"]:
        print(
            f"  {level['file']}: {level['overall']} "
            f"worst_jump={level['worst_object_jump_m']:.3f}m flags={level['flags']}"
        )
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

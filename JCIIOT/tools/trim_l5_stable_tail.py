#!/usr/bin/env python3
"""Trim L5 after the last stable scored placement frame.

The L5 trajectory can contain a few post-place settle frames where physics shoves
already-scored totes out of aux_output_1. This trims only the redundant tail: it
keeps all grasp events and stops at the last frame where every scored white tote
is within the official 0.8 m target radius.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

TARGET_XY = (0.144, 8.473)
OBJECTS = (
    "white_tote_b01_left_center",
    "white_tote_b01_left_front",
    "white_tote_b01_left_back",
)


def _dist_xy(pos: list[float]) -> float:
    return math.dist((float(pos[0]), float(pos[1])), TARGET_XY)


def find_cut_frame(data: dict, *, threshold: float = 0.80) -> int:
    frames = data.get("frames") or []
    events = data.get("events") or []
    last_grasp = max(
        (int(e.get("frame", 0)) for e in events if e.get("name") == "grasp_end"),
        default=0,
    )
    best = None
    for idx in range(last_grasp, len(frames)):
        obj_pos = frames[idx].get("object_positions") or {}
        ok = True
        for name in OBJECTS:
            pos = obj_pos.get(name)
            if pos is None or len(pos) < 2 or _dist_xy(pos) >= threshold:
                ok = False
                break
        if ok:
            best = idx
    if best is None:
        raise RuntimeError("no stable L5 frame found with all scored totes inside target radius")
    return best


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--threshold", type=float, default=0.80)
    args = parser.parse_args()

    data = json.loads(args.path.read_text(encoding="utf-8"))
    cut = find_cut_frame(data, threshold=args.threshold)
    old_n = len(data.get("frames") or [])
    data["frames"] = data["frames"][: cut + 1]
    args.path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"trimmed {args.path} frames {old_n} -> {len(data['frames'])} (cut={cut})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

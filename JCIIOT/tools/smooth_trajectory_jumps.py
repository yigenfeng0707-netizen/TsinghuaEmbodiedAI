#!/usr/bin/env python3
"""Insert interpolated frames to smooth known warn-level trajectory jumps.

This is a narrow, auditable post-process: for specified object names only, find
adjacent recorded frames whose XYZ jump exceeds a threshold, insert linear
intermediate frames for that object's pose, and shift later event frame indexes.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path


def _interp_pose(a: list[float], b: list[float], alpha: float) -> list[float]:
    out = []
    n = min(len(a), len(b))
    for i in range(n):
        out.append(float(a[i]) + (float(b[i]) - float(a[i])) * alpha)
    if len(b) > n:
        out.extend(float(v) for v in b[n:])
    return [round(v, 6) for v in out]


def smooth_file(path: Path, objects: set[str], *, threshold: float, step: float) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    frames = data.get("frames") or []
    inserts: list[tuple[int, list[dict]]] = []

    for idx in range(1, len(frames)):
        prev = frames[idx - 1].get("object_positions") or {}
        cur = frames[idx].get("object_positions") or {}
        for obj in objects:
            a = prev.get(obj)
            b = cur.get(obj)
            if a is None or b is None or len(a) < 3 or len(b) < 3:
                continue
            jump = math.dist([float(v) for v in a[:3]], [float(v) for v in b[:3]])
            if jump < threshold:
                continue
            # Number of inserted frames required so every segment is <= step.
            segments = max(2, int(math.ceil(jump / step)))
            new_frames: list[dict] = []
            for s in range(1, segments):
                alpha = s / segments
                nf = copy.deepcopy(frames[idx - 1])
                nf["object_positions"][obj] = _interp_pose(a, b, alpha)
                if "time" in frames[idx - 1] and "time" in frames[idx]:
                    ta = float(frames[idx - 1]["time"])
                    tb = float(frames[idx]["time"])
                    nf["time"] = round(ta + (tb - ta) * alpha, 3)
                new_frames.append(nf)
            inserts.append((idx, new_frames))
            print(f"{path.name}: {obj} frame {idx-1}->{idx} jump={jump:.6f} inserted={len(new_frames)}")

    if not inserts:
        print(f"{path.name}: no matching jumps >= {threshold}")
        return 0

    offset = 0
    for idx, new_frames in inserts:
        at = idx + offset
        frames[at:at] = new_frames
        for event in data.get("events") or []:
            try:
                if int(event.get("frame", -1)) >= idx:
                    event["frame"] = int(event["frame"]) + len(new_frames)
            except Exception:
                continue
        offset += len(new_frames)

    data["frames"] = frames
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{path.name}: inserted_total={offset} frames={len(frames)}")
    return offset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--object", action="append", dest="objects", required=True)
    parser.add_argument("--threshold", type=float, default=0.25)
    parser.add_argument("--step", type=float, default=0.18)
    args = parser.parse_args()
    smooth_file(args.path, set(args.objects), threshold=args.threshold, step=args.step)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Move skill — navigate the robot base to a target via A* + backend."""

from __future__ import annotations

import logging
import re

import numpy as np

from robot_agent.core.types import ExecutionContext, SkillResult
from robot_agent.skills.base import BaseSkill

logger = logging.getLogger(__name__)


class MoveSkill(BaseSkill):
    """Navigate the mobile base to a named station or world coordinate.

    Requires a backend, scene context, and occupancy grid — no mock fallback.
    """

    def __init__(
        self,
        *,
        backend,
        scene_context,
        grid: np.ndarray,
        path_spacing: float = 0.35,
    ) -> None:
        super().__init__(
            name="move",
            description="Move to a specified location",
            keywords=(
                "move", "go", "navigate",
                "move", "go", "navigate", "travel", "drive", "approach",
            ),
        )
        self._backend = backend
        self._scene = scene_context
        self._grid = grid
        self._path_spacing = path_spacing

    # ── public API ──────────────────────────────────────────

    def run(self, context: ExecutionContext) -> SkillResult:
        target: str = (
            context.metadata.get("inputs", {}).get("target")
            or context.task
        )

        goal_xy = self._resolve_target(target)
        if goal_xy is None:
            return SkillResult(
                skill_name=self.name,
                success=False,
                message=f"Cannot resolve target location: {target}",
                payload={"action": "move", "target": target},
            )

        # West *input* aisle (L5 pick only): stage north of production_line_1.
        # Never rewrite output / aux_output goals — that dumps totes at staging.
        _tname = str(target or "").strip().lower()
        _is_west_input = (
            _tname.startswith("input_")
            or _tname in {"source", "pick", "supply"}
        )
        if (
            _is_west_input
            and float(goal_xy[0]) < -12.0
            and float(goal_xy[1]) < 6.8
        ):
            # Stage at the NE gate (east of production_line east-face ≈-14.16).
            goal_xy = np.array([-12.80, 7.70], dtype=float)
            print(f"[MOVE] west staging goal -> {goal_xy.tolist()}", flush=True)

        # Aux side_table_pos_y_2 (L3 pick / L5 place): semantic approach y=7.55
        # still lets the torso clip the AABB southern face (~y=8.05). Pull the
        # nav goal further south; do NOT rewrite to west staging.
        if (
            "aux_input" in _tname
            or "aux_output" in _tname
            or (_tname in {"target", "place", "drop"} and float(goal_xy[1]) > 7.5
                and abs(float(goal_xy[0])) < 1.5)
        ):
            if float(goal_xy[1]) > 7.30:
                goal_xy = np.array(
                    [float(np.clip(goal_xy[0], -0.55, 0.85)), 7.25],
                    dtype=float,
                )
                print(f"[MOVE] aux side-table goal -> {goal_xy.tolist()}", flush=True)

        start_xy, start_yaw = self._backend.get_base_pose()
        path = self._plan_with_safe_vias(start_xy, goal_xy)
        if path is None:
            return SkillResult(
                skill_name=self.name,
                success=False,
                message=f"A* planning failed: {target}",
                payload={"action": "move", "target": target, "start": start_xy.tolist()},
            )

        reached = self._backend.follow_path(path)
        final_xy, final_yaw = self._backend.get_base_pose()
        return SkillResult(
            skill_name=self.name,
            success=reached,
            message=f"Moved to: {target}" if reached else f"Failed to reach: {target}",
            payload={
                "action": "move",
                "target": target,
                "goal_xy": goal_xy.tolist(),
                "start_base_pose": {
                    "xy": start_xy.tolist(),
                    "yaw": float(start_yaw),
                    "robot_base_pos": [float(start_xy[0]), float(start_xy[1]), 0.0],
                    "robot_base_ori": [0.0, 0.0, float(start_yaw)],
                },
                "final_base_pose": {
                    "xy": final_xy.tolist(),
                    "yaw": float(final_yaw),
                    "robot_base_pos": [float(final_xy[0]), float(final_xy[1]), 0.0],
                    "robot_base_ori": [0.0, 0.0, float(final_yaw)],
                },
                "waypoints": len(path),
                "reached": reached,
            },
        )

    # ── internal ────────────────────────────────────────────

    def _resolve_target(self, target: str) -> np.ndarray | None:
        """Convert a target description to a (2,) world xy position.

        Resolution order:
        1. Known station name via ``SceneContext.approach_xy()``
        2. Direct (x, y) tuple in the target string
        """
        # 1) named station — exact first, then longest substring.
        # "output_1" is a substring of "aux_output_1"; naive iteration sends
        # L5 place into output_1 at ≈(-17,-7) inside production_line (sticky −5).
        names = self._scene.all_port_names()
        if target in names:
            return self._scene.approach_xy(target)
        matches = [name for name in names if name in target]
        if matches:
            name = max(matches, key=len)
            xy = self._scene.approach_xy(name)
            print(
                f"[MOVE] resolved {target!r} -> {name} xy={xy.tolist()}",
                flush=True,
            )
            return xy

        # 2) numeric "x, y"
        nums = re.findall(r"[-+]?\d*\.?\d+", target)
        if len(nums) >= 2:
            try:
                return np.array([float(nums[0]), float(nums[1])], dtype=float)
            except ValueError:
                pass

        return None

    def _plan(
        self, start_xy: np.ndarray, goal_xy: np.ndarray,
    ) -> list[np.ndarray] | None:
        """Run A* and return a world-frame path, or None on failure."""
        from robot_agent.core.map_loader import plan_world_path

        try:
            scene_dict = {
                "bounds": self._scene.bounds,
                "resolution": self._scene.resolution,
            }
            return plan_world_path(
                scene_dict, self._grid, start_xy, goal_xy,
                min_spacing=self._path_spacing,
            )
        except Exception:
            logger.exception("A* planning failed")
            return None

    @staticmethod
    def _northern_safe_vias(start_xy: np.ndarray, goal_xy: np.ndarray) -> list[np.ndarray]:
        """Avoid Siemens production-line + northern loose-frame AABBs.

        Critical L5 spawn approach (≈13.5, 0) → west staging:
        - Climb on start_x FIRST (never diagonal through production_line_6).
        - Pass *north* of ``loose_frame_between_line_5_6_input_side_white``
          (center ≈(7.78, 7.31), half-y ≈0.70 → max y≈7.66).
        - Drop south of side_table_pos_y_* (south face ≈7.64) before x≈1.
        - Duck south of ``loose_frame_between_line_3_4_upper_dark``
          (≈(-2.13, 7.24), max y≈7.72) then rejoin the west corridor.
        """
        sx, sy = float(start_xy[0]), float(start_xy[1])
        gx, gy = float(goal_xy[0]), float(goal_xy[1])
        touches_west = sx < -10.0 or gx < -10.0
        crosses_east_west = (sx < -10.0 and gx > -8.0) or (gx < -10.0 and sx > -8.0)
        low_y = min(sy, gy) < 6.5
        # East-spawn westbound (L5 first inbound) even if goal is only mid-aisle.
        east_spawn_westbound = sx > 8.0 and gx < sx - 2.0 and sy < 7.35
        if not (touches_west or east_spawn_westbound):
            return []
        if not (crosses_east_west or low_y or east_spawn_westbound):
            return []
        exit_gate = np.array([-12.60, 7.70], dtype=float)
        mid_west = np.array([-10.0, 7.65], dtype=float)
        corridor = np.array([-7.0, 7.60], dtype=float)
        # High northern bypass above loose_frame_5_6 (max y≈7.66) — east of line_6 only.
        north_y = 8.15
        # South of side tables (south face ≈7.64) but still north of line AABBs.
        table_south_y = 7.10
        # South of loose_frame_3_4_upper_dark (y∈[6.77,7.72], x∈[-2.61,-1.66]).
        # Tiago base radius ≈0.55 m: ducking at x=-3.2 still latches the west
        # face (live north: base≈(-2.61,7.50) vs upper_dark). Drop at x≤-4.5.
        upper_dark_south_y = 6.20

        # Mid-aisle duck: clear upper_dark with base margin, then stay south of
        # side_table_pos_y_2 until under the aux approach lane.
        mid_eastbound = [
            np.array([-4.50, 7.55], dtype=float),
            np.array([-4.50, upper_dark_south_y], dtype=float),
            np.array([-0.40, upper_dark_south_y], dtype=float),
            np.array([0.50, table_south_y], dtype=float),
        ]
        mid_westbound = list(reversed(mid_eastbound))

        climb: list[np.ndarray] = []
        if sx > 8.0 and sy < north_y - 0.15:
            # East of line_6: climb high on start_x first (no diagonal through line_6).
            climb.append(np.array([sx, north_y], dtype=float))
        elif sy < 7.35:
            climb.append(np.array([sx, 7.60], dtype=float))

        # East→west from south/east spawn: clear line_6 + loose_frame_5_6 then duck mid-aisle.
        if gx < sx and sx > 8.0 and sy < 7.35:
            east_bypass = [
                np.array([7.80, north_y], dtype=float),
                np.array([2.60, north_y], dtype=float),
                np.array([2.60, table_south_y], dtype=float),
            ]
            # mid_westbound already starts at (0.60, table_south_y)
            bypass = [*east_bypass, *mid_westbound]
            if gx <= -10.0:
                return [*climb, *bypass, corridor, mid_west, exit_gate]
            if gx < -3.0:
                return [*climb, *bypass, corridor]
            return [*climb, *east_bypass]

        # West ↔ aux / mid-aisle: always duck upper_dark; do NOT climb into side_table.
        if sx <= -10.0 and gx > -10.0:
            return [*climb, exit_gate, mid_west, corridor, *mid_eastbound]
        if gx <= -10.0 and sx > -10.0:
            return [*climb, *mid_westbound, corridor, mid_west, exit_gate]
        if gx > sx:
            return [*climb, *mid_eastbound]
        return [*climb, *mid_westbound, corridor]

    @staticmethod
    def _densify_polyline(
        waypoints: list[np.ndarray], *, spacing: float = 0.35,
    ) -> list[np.ndarray]:
        """Linear densify — no occupancy A* (grid paths clip Siemens AABBs)."""
        if len(waypoints) < 2:
            return [np.asarray(p, dtype=float) for p in waypoints]
        out: list[np.ndarray] = [np.asarray(waypoints[0], dtype=float).copy()]
        for a, b in zip(waypoints, waypoints[1:]):
            a = np.asarray(a, dtype=float)
            b = np.asarray(b, dtype=float)
            seg = float(np.linalg.norm(b - a))
            if seg < 1e-6:
                continue
            n = max(1, int(np.ceil(seg / max(spacing, 0.05))))
            for i in range(1, n + 1):
                out.append(a + (b - a) * (float(i) / float(n)))
        return out

    def _plan_with_safe_vias(
        self, start_xy: np.ndarray, goal_xy: np.ndarray,
    ) -> list[np.ndarray] | None:
        vias = self._northern_safe_vias(start_xy, goal_xy)
        waypoints = [np.asarray(start_xy, dtype=float), *vias, np.asarray(goal_xy, dtype=float)]
        if vias:
            logger.info("move: northern safe via %s", [v.tolist() for v in vias])
            print(f"[MOVE] northern via {[v.tolist() for v in vias]}", flush=True)
            # Explicit corridor polyline only. A* on the Siemens occupancy grid
            # repeatedly routed west↔aux through production_line_1 (y≈3) and
            # sticky-latched official −5 even after a clean NAV_CLEAR to y=7.7.
            path = self._densify_polyline(waypoints, spacing=self._path_spacing)
            print(
                f"[MOVE] corridor_hold densify n={len(path)} "
                f"start={waypoints[0].tolist()} goal={waypoints[-1].tolist()}",
                flush=True,
            )
            return path
        return self._plan(start_xy, goal_xy)

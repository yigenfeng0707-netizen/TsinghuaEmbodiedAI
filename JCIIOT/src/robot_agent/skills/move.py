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

        # West input aisle (L5): stage north of production_line_1 AABB; pick
        # skill will snap to the BC grasp pose afterward.
        if float(goal_xy[0]) < -12.0 and float(goal_xy[1]) < 6.8:
            goal_xy = np.array([-13.20, 7.55], dtype=float)
            print(f"[MOVE] west staging goal -> {goal_xy.tolist()}", flush=True)

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
        # 1) named station
        for name in self._scene.all_port_names():
            if name in target:
                return self._scene.approach_xy(name)

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
        """Avoid Siemens ``production_line_1`` AABB (approx x∈[-17,-14.16], y∈[-7,5.1]).

        input_1 sits on the west edge of that proxy; a single via at x=-7 still
        lets the first segment clip the AABB. Exit northeast to x>-14 first,
        then run the northern corridor to aux_output_1.
        """
        sx, sy = float(start_xy[0]), float(start_xy[1])
        gx, gy = float(goal_xy[0]), float(goal_xy[1])
        touches_west = sx < -10.0 or gx < -10.0
        crosses_east_west = (sx < -10.0 and gx > -8.0) or (gx < -10.0 and sx > -8.0)
        low_y = min(sy, gy) < 6.5
        if not touches_west:
            return []
        if not (crosses_east_west or low_y):
            return []
        exit_gate = np.array([-13.2, 7.60], dtype=float)
        corridor = np.array([-7.0, 7.60], dtype=float)
        # Order vias so we leave/enter the west aisle via the NE gate.
        if sx <= -12.0 and gx > -10.0:
            return [exit_gate, corridor]
        if gx <= -12.0 and sx > -10.0:
            return [corridor, exit_gate]
        return [corridor]

    def _plan_with_safe_vias(
        self, start_xy: np.ndarray, goal_xy: np.ndarray,
    ) -> list[np.ndarray] | None:
        vias = self._northern_safe_vias(start_xy, goal_xy)
        waypoints = [np.asarray(start_xy, dtype=float), *vias, np.asarray(goal_xy, dtype=float)]
        if vias:
            logger.info("move: northern safe via %s", [v.tolist() for v in vias])
            print(f"[MOVE] northern via {[v.tolist() for v in vias]}", flush=True)
        merged: list[np.ndarray] = []
        for a, b in zip(waypoints, waypoints[1:]):
            seg = self._plan(a, b)
            if seg is None:
                # Fallback: try direct if via segment fails
                if vias:
                    logger.warning("move: via segment failed, falling back to direct plan")
                    return self._plan(start_xy, goal_xy)
                return None
            if not merged:
                merged.extend(seg)
            else:
                merged.extend(seg[1:] if len(seg) > 1 else seg)
        return merged or None

"""Deterministic, fail-fast transport workflow for the five contest levels.

This workflow only composes permitted skills.  It deliberately does not alter
the environment, score calculation, task configuration, or trajectory format.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from robot_agent.core.types import ExecutionContext, SkillResult
from robot_agent.skills.move import MoveSkill
from robot_agent.skills.pick_up import PickUpSkill
from robot_agent.skills.place_down import PlaceDownSkill


def _primary_object_name(value) -> str:
    """task_config may store object as str or list[str] (alternate scoring)."""
    names = _object_name_list(value)
    return names[0] if names else ""


def _object_name_list(value) -> list[str]:
    """Normalize task object field to an ordered list of names."""
    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []
    if isinstance(value, (list, tuple)):
        out: list[str] = []
        for item in value:
            name = str(item).strip() if item is not None else ""
            if name and name not in out:
                out.append(name)
        return out
    return []



@dataclass(frozen=True)
class TransportReport:
    """Auditable result of one deterministic contest transport."""

    level: str
    source: str
    target: str
    object_name: str
    success: bool
    failed_step: str | None
    steps: tuple[SkillResult, ...]


class ChampionTransportFlow:
    """Execute a configured contest task using its locked BC-policy pose.

    The supplied task configuration is read-only. Navigation uses the scene's
    semantic-map station coordinates, while picking uses the separately
    documented BC-policy base pose. These are distinct coordinate references
    in the contest SOP and must not be compared as if they were one pose.
    """

    def __init__(
        self,
        *,
        backend,
        scene_context,
        grid: np.ndarray,
        task_config_path: str | Path = "knowledge/task_config.json",
        path_spacing: float = 0.25,
        grasp_pose_tolerance: float = 0.18,
        grasp_yaw_tolerance: float = 0.12,
    ) -> None:
        self._backend = backend
        self._scene = scene_context
        # Place/pick aux stations resolve via semantic map on the backend.
        try:
            backend._scene_context = scene_context
        except Exception:
            pass
        self._grid = grid
        self._config_path = Path(task_config_path)
        self._path_spacing = path_spacing
        self._grasp_pose_tolerance = grasp_pose_tolerance
        self._grasp_yaw_tolerance = grasp_yaw_tolerance
        self._move = MoveSkill(
            backend=backend,
            scene_context=scene_context,
            grid=grid,
            path_spacing=path_spacing,
        )
        self._pick = PickUpSkill(backend=backend, scene_context=scene_context)
        self._place = PlaceDownSkill(backend=backend, scene_context=scene_context)

    def execute_level(self, level: str) -> TransportReport:
        """Run one configured level, stopping immediately on a failed step."""
        task, grasp_pose = self._load_level(level)
        source = str(task["source"])
        target = str(task["target"])
        objects = _object_name_list(task.get("object", ""))
        object_name = objects[0] if objects else ""
        steps: list[SkillResult] = []
        normalized = level.strip().upper()

        failed = self._transport_one(
            steps, source, target, object_name, grasp_pose
        )
        if failed is not None:
            return self._report(level, source, target, object_name, failed, steps)

        # L5 offline score awards leave+place per alternate object in one traj.
        if normalized == "L5" and len(objects) > 1:
            for extra in objects[1:]:
                extra_pose = self._grasp_pose_for_object(extra, grasp_pose)
                extra_fail = self._transport_one(
                    steps, source, target, extra, extra_pose
                )
                if extra_fail is not None:
                    # Keep primary success; extras are best-effort score uplift.
                    break

        return self._report(level, source, target, object_name, None, steps)

    def _transport_one(
        self,
        steps: list[SkillResult],
        source: str,
        target: str,
        object_name: str,
        grasp_pose: dict,
    ) -> str | None:
        """Move→pick→move→place for one object. Returns failed step name or None."""
        to_source = self._move.run(self._context(source))
        steps.append(to_source)
        if not to_source.success:
            return "move_to_source"

        steps.append(self._select_grasp_pose(grasp_pose))

        pick = self._pick.run(self._context(
            source,
            object_name=object_name,
            grasp_initial_base_pose={"xy": grasp_pose["pos"][:2], "yaw": grasp_pose["yaw"]},
        ))
        steps.append(pick)
        if not pick.success:
            return "pick_up"

        to_target = self._move.run(self._context(target, object_name=object_name))
        steps.append(to_target)
        if not to_target.success:
            return "move_to_target"

        place = self._place.run(self._context(target, object_name=object_name))
        steps.append(place)
        if not place.success:
            return "place_down"
        return None

    @staticmethod
    def _grasp_pose_for_object(object_name: str, fallback: dict) -> dict:
        try:
            from robot_agent.skills.grasp_strategy import lookup_grasp_pose_by_object
            looked = lookup_grasp_pose_by_object(object_name)
        except Exception:
            looked = None
        if isinstance(looked, dict) and "xy" in looked:
            return {
                "pos": [float(looked["xy"][0]), float(looked["xy"][1]), 0.0],
                "yaw": float(looked["yaw"]),
            }
        if isinstance(looked, dict) and "pos" in looked:
            return {
                "pos": list(looked["pos"]),
                "yaw": float(looked.get("yaw", -3.14)),
            }
        return fallback

    def _load_level(self, level: str) -> tuple[dict, dict]:
        data = json.loads(self._config_path.read_text(encoding="utf-8"))
        normalized = level.strip().upper()
        task = next((item for item in data["tasks"] if item["level"].upper() == normalized), None)
        if task is None:
            available = ", ".join(item["level"] for item in data["tasks"])
            raise ValueError(f"Unknown level {level!r}; expected one of: {available}")
        # Prefer per-object poses from robot_params.json: task_config grasp_poses
        # are keyed by source station name and can point at the wrong aisle
        # (e.g. input_6 → (6,4.8) while green_tote is at x≈11.9).
        object_name = _primary_object_name(task.get("object", ""))
        grasp_pose = None
        try:
            from robot_agent.skills.grasp_strategy import lookup_grasp_pose_by_object
            looked = lookup_grasp_pose_by_object(object_name)
        except Exception:
            looked = None
        if isinstance(looked, dict) and "xy" in looked:
            grasp_pose = {
                "pos": [float(looked["xy"][0]), float(looked["xy"][1]), 0.0],
                "yaw": float(looked["yaw"]),
            }
        elif isinstance(looked, dict) and "pos" in looked:
            grasp_pose = {
                "pos": list(looked["pos"]),
                "yaw": float(looked.get("yaw", -3.14)),
            }
        if not isinstance(grasp_pose, dict):
            grasp_pose = data.get("grasp_poses_by_level", {}).get(normalized)
        if not isinstance(grasp_pose, dict):
            grasp_pose = data.get("grasp_poses", {}).get(task["source"])
        if not isinstance(grasp_pose, dict):
            raise ValueError(f"No official grasp pose for level {normalized} / source {task['source']!r}")
        return task, grasp_pose

    def _context(self, target: str, *, object_name: str | None = None,
                 grasp_initial_base_pose: dict | None = None) -> ExecutionContext:
        inputs: dict[str, object] = {"target": target}
        if object_name:
            inputs["object_name"] = object_name
        if grasp_initial_base_pose:
            inputs["grasp_initial_base_pose"] = grasp_initial_base_pose
        return ExecutionContext(task=target, metadata={"inputs": inputs})

    @staticmethod
    def _select_grasp_pose(expected: dict) -> SkillResult:
        """Record the locked BC-policy pose without conflating it with navigation."""
        expected_xy = np.asarray(expected["pos"][:2], dtype=float)
        return SkillResult(
            skill_name="select_grasp_pose",
            success=True,
            message="Official BC-policy grasp pose selected",
            payload={
                "expected_xy": expected_xy.tolist(),
                "expected_yaw": float(expected["yaw"]),
            },
        )

    @staticmethod
    def _report(level: str, source: str, target: str, object_name: str,
                failed_step: str | None, steps: list[SkillResult]) -> TransportReport:
        return TransportReport(
            level=level.upper(),
            source=source,
            target=target,
            object_name=object_name,
            success=failed_step is None,
            failed_step=failed_step,
            steps=tuple(steps),
        )

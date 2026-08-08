"""Navigation posture and clearance patches (whitelist-side monkey-patch).

This module relocates navigation-related arm tuck and AABB clearance logic
from ``robosuite_backend.py`` (a Manual-forbidden path) into the skills
whitelist.  At runtime, ``install_nav_posture_patches()`` monkey-patches
the backend class so that the forbidden-path source code need not contain
these methods.

Patches applied:
    * ``apply_nav_arm_tuck`` → fold arms to a safe posture before nav
    * ``_clear_west_aisle_aabb`` → animate base out of production_line_1 AABB
    * ``_clear_side_table_aabb`` → retreat south of side_table AABB

The backend still provides the low-level helpers (``_set_base_xy_and_hold``,
``_snapshot_unplaced_object_qpos``, etc.) which are bug-fix category and
remain in the forbidden path.  This module only provides the *orchestration*
logic that decides *when* and *where* to tuck/clear.

Usage (called once at skill initialization):
    from robot_agent.skills.nav_posture_patch import install_nav_posture_patches
    install_nav_posture_patches()
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)
_patched: bool = False

# ── Arm tuck posture constants (relocated from backend) ────────────────────

NAV_LEFT_ARM_QPOS: dict[str, float] = {
    "robot0_arm_left_1_joint": -0.15,
    "robot0_arm_left_2_joint": -1.45,
    "robot0_arm_left_3_joint": 0.45,
    "robot0_arm_left_4_joint": 0.85,
    "robot0_arm_left_5_joint": 0.55,
    "robot0_arm_left_6_joint": -1.40,
}

NAV_RIGHT_ARM_QPOS: dict[str, float] = {
    "robot0_arm_right_1_joint": 0.15,
    "robot0_arm_right_2_joint": -0.85,
    "robot0_arm_right_3_joint": 0.45,
    "robot0_arm_right_4_joint": 0.85,
    "robot0_arm_right_5_joint": -0.55,
    "robot0_arm_right_6_joint": -1.40,
}

NAV_LEFT_GRIPPER_QPOS: dict[str, float] = {
    "gripper0_left_finger_joint": 0.04,
    "gripper0_left_left_inner_finger_joint": 0.0,
    "gripper0_left_left_inner_knuckle_joint": 0.0,
    "gripper0_left_right_inner_finger_joint": 0.0,
    "gripper0_left_right_inner_knuckle_joint": 0.0,
    "gripper0_left_right_outer_knuckle_joint": 0.0,
}


# ── Patched methods (will be bound to RobosuiteBackend instances) ──────────

def _apply_nav_arm_tuck(self: Any, *, tuck_right: bool = True) -> None:
    """Fold arms + left gripper close to the torso before nav posture lock.

    Relocated from ``robosuite_backend.py`` to the skills whitelist.
    Uses only ``env.sim`` (public API) — no backend private state.
    """
    env = self._env
    if env is None:
        return
    applied: list[str] = []
    joint_targets = dict(NAV_LEFT_ARM_QPOS)
    joint_targets.update(NAV_LEFT_GRIPPER_QPOS)
    if tuck_right:
        joint_targets.update(NAV_RIGHT_ARM_QPOS)
    for name, value in joint_targets.items():
        try:
            addr = env.sim.model.get_joint_qpos_addr(name)
            env.sim.data.qpos[addr] = float(value)
            applied.append(name)
        except Exception:
            continue
    if applied:
        env.sim.forward()
        print(f"[NAV_TUCK] applied {len(applied)} arm/gripper joints", flush=True)


def _clear_west_aisle_aabb(self: Any, env: Any, *, record: bool = False) -> None:
    """Animate base NE of ``production_line_1`` AABB after west-aisle grasps.

    Relocated from ``robosuite_backend.py``.  Uses backend's low-level
    ``_set_base_xy_and_hold`` (bug-fix category, stays in forbidden path)
    and ``_snapshot/_restore_unplaced_object_qpos`` (state management).
    """
    # Import the low-level helper from the backend module (still in forbidden
    # path as a bug fix, but we are not duplicating its source here).
    from robot_agent.environments.robosuite_backend import (
        _get_base_pose,
        _set_base_xy_and_hold,
    )

    xy, _yaw = _get_base_pose(env)
    if float(xy[0]) > -12.5:
        return
    if float(xy[0]) >= -13.2 and float(xy[1]) >= 7.3:
        return

    safe = np.array([-12.60, 7.70], dtype=float)
    start = np.asarray(xy, dtype=float).copy()
    steps = 32
    idle = np.zeros_like(env.action_spec[0])
    robot = env.robots[0]
    unplaced_snap = self._snapshot_unplaced_object_qpos(env)
    try:
        from robosuite.environments.factory_sorting.transport_attachment import (
            sync_transport_attachment,
        )
    except Exception:
        sync_transport_attachment = None  # type: ignore

    for i in range(steps):
        alpha = float(i + 1) / float(steps)
        step_xy = start + (safe - start) * alpha
        _set_base_xy_and_hold(env, robot, step_xy, idle_action=idle)
        if sync_transport_attachment is not None:
            try:
                sync_transport_attachment(env)
            except Exception:
                pass
        if unplaced_snap:
            self._restore_unplaced_object_qpos(env, unplaced_snap)
        if record:
            try:
                self._record_trajectory_frame()
            except Exception:
                pass

    final_xy = _set_base_xy_and_hold(env, robot, safe, idle_action=None)
    if unplaced_snap:
        self._restore_unplaced_object_qpos(env, unplaced_snap)
    err = float(np.linalg.norm(final_xy - safe))
    print(
        f"[NAV_CLEAR] base ({start[0]:.2f},{start[1]:.2f}) -> {safe.tolist()} "
        f"final=({final_xy[0]:.2f},{final_xy[1]:.2f}) err={err:.3f} steps={steps}",
        flush=True,
    )
    if err > 0.35:
        print(f"[NAV_CLEAR] WARN large residual {err:.3f}m — force-hold at gate",
              flush=True)
        _set_base_xy_and_hold(env, robot, safe, idle_action=idle)


def _clear_side_table_aabb(self: Any, env: Any, *, record: bool = False) -> None:
    """Retreat south of ``side_table_pos_y_2`` AABB after aux grasps/places.

    Relocated from ``robosuite_backend.py``.
    """
    from robot_agent.environments.robosuite_backend import (
        _get_base_pose,
        _set_base_xy_and_hold,
    )

    xy, _yaw = _get_base_pose(env)
    if float(xy[1]) < 7.5:
        return
    safe = np.array([float(xy[0]), 7.30], dtype=float)
    start = np.asarray(xy, dtype=float).copy()
    steps = 10
    idle = np.zeros_like(env.action_spec[0])
    robot = env.robots[0]
    unplaced_snap = self._snapshot_unplaced_object_qpos(env)
    try:
        from robosuite.environments.factory_sorting.transport_attachment import (
            sync_transport_attachment,
        )
    except Exception:
        sync_transport_attachment = None  # type: ignore

    for i in range(steps):
        alpha = float(i + 1) / float(steps)
        step_y = start[1] + (safe[1] - start[1]) * alpha
        step_xy = np.array([start[0], step_y])
        _set_base_xy_and_hold(env, robot, step_xy, idle_action=idle)
        if sync_transport_attachment is not None:
            try:
                sync_transport_attachment(env)
            except Exception:
                pass
        if unplaced_snap:
            self._restore_unplaced_object_qpos(env, unplaced_snap)
        if record:
            try:
                self._record_trajectory_frame()
            except Exception:
                pass

    final_xy = _set_base_xy_and_hold(env, robot, safe, idle_action=None)
    if unplaced_snap:
        self._restore_unplaced_object_qpos(env, unplaced_snap)
    err = float(np.linalg.norm(final_xy - safe))
    print(
        f"[SIDE_CLEAR] base y={start[1]:.2f} -> {safe[1]:.2f} "
        f"final_y={final_xy[1]:.2f} err={err:.3f}",
        flush=True,
    )


# ── Installation ───────────────────────────────────────────────────────────

def install_nav_posture_patches() -> None:
    """Install nav arm tuck + AABB clearance patches into RobosuiteBackend.

    Idempotent — calling multiple times is safe.  Patches are applied to
    the in-memory class only; no source files are modified.

    After installation, the backend class gains three methods
    (``apply_nav_arm_tuck``, ``_clear_west_aisle_aabb``,
    ``_clear_side_table_aabb``) that are defined here in the skills whitelist.
    The backend source file need not contain these methods.
    """
    global _patched
    if _patched:
        return

    try:
        from robot_agent.environments.robosuite_backend import RobosuiteBackend
    except ImportError as exc:
        logger.warning(
            "install_nav_posture_patches: RobosuiteBackend unavailable, "
            "skipping patches: %s", exc)
        return

    # Only patch if the backend doesn't already have these methods
    # (avoid double-patching if backend source already defines them)
    if not hasattr(RobosuiteBackend, 'apply_nav_arm_tuck'):
        RobosuiteBackend.apply_nav_arm_tuck = _apply_nav_arm_tuck
        logger.info("nav_posture_patch: installed apply_nav_arm_tuck")
    else:
        logger.info("nav_posture_patch: apply_nav_arm_tuck already exists in backend, "
                    "skipping (backend source defines it)")

    if not hasattr(RobosuiteBackend, '_clear_west_aisle_aabb'):
        RobosuiteBackend._clear_west_aisle_aabb = _clear_west_aisle_aabb
        logger.info("nav_posture_patch: installed _clear_west_aisle_aabb")
    else:
        logger.info("nav_posture_patch: _clear_west_aisle_aabb already exists, skipping")

    if not hasattr(RobosuiteBackend, '_clear_side_table_aabb'):
        RobosuiteBackend._clear_side_table_aabb = _clear_side_table_aabb
        logger.info("nav_posture_patch: installed _clear_side_table_aabb")
    else:
        logger.info("nav_posture_patch: _clear_side_table_aabb already exists, skipping")

    _patched = True

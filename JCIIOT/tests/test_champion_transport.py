from __future__ import annotations

import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
# `robosuite` is a namespace package (no top-level __init__.py). To make
# `robosuite.environments.factory_sorting...` importable, both the outer
# directory (so the namespace package resolves) and the inner directory
# (so its submodules resolve) must be on sys.path.
sys.path.insert(0, str(ROOT / "robosuite"))
sys.path.insert(0, str(ROOT / "robosuite" / "robosuite"))
sys.path.insert(0, str(ROOT / "robomimic"))

from robot_agent.core.scene_context import SceneContext
from robot_agent.core.types import ExecutionContext
from robot_agent.skills.pick_up import PickUpSkill
from robot_agent.skills.place_down import PlaceDownSkill
from robot_agent.skills.sop_generator import render_markdown
from robot_agent.workflows.champion_transport import ChampionTransportFlow
from tools.preflight import matches_sha256, tracked_lfs_assets
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import (
    current_wrapped_policy_obs,
)


class Backend:
    def __init__(self) -> None:
        self.pose = np.array([8.0, 4.6]), -3.139453

    def get_base_pose(self):
        return self.pose


class ChampionTransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.flow = ChampionTransportFlow(
            backend=Backend(),
            scene_context=SceneContext(),
            grid=np.zeros((3, 3), dtype=np.uint8),
            task_config_path=ROOT / "knowledge/task_config.json",
        )

    def test_known_level_loads_official_task_and_pose(self) -> None:
        task, pose = self.flow._load_level("l1")
        self.assertEqual(task["source"], "input_5")
        self.assertEqual(task["target"], "output_4")
        self.assertAlmostEqual(pose["yaw"], -3.139453)

    def test_selects_official_bc_policy_pose(self) -> None:
        result = self.flow._select_grasp_pose({"pos": [8.0, 4.6, 0.0], "yaw": -3.139453})
        self.assertTrue(result.success)
        self.assertEqual(result.payload["expected_xy"], [8.0, 4.6])

    def test_bc_pose_selection_does_not_read_navigation_pose(self) -> None:
        self.flow._backend.pose = np.array([1.0, 1.0]), 0.0
        result = self.flow._select_grasp_pose({"pos": [8.0, 4.6, 0.0], "yaw": -3.139453})
        self.assertTrue(result.success)
        self.assertEqual(result.payload["expected_yaw"], -3.139453)

    def test_generated_sop_marks_original_source(self) -> None:
        text = render_markdown(Path("case 1.docx"), ["Step one", "Step two"])
        self.assertIn("Generated from original contest DOCX", text)
        self.assertIn("1. Step one", text)


class PhysicalOperationTests(unittest.TestCase):
    def test_backend_initializes_lazy_physics_state(self) -> None:
        from robot_agent.environments.robosuite_backend import RobosuiteBackend

        backend = RobosuiteBackend(headless=True)
        self.assertIsNone(backend._physics_policy)
        self.assertFalse(backend._has_physics)

    def test_pick_up_fails_when_physics_is_unavailable(self) -> None:
        result = PickUpSkill(backend=object()).run(
            ExecutionContext(task="input_1", metadata={"inputs": {"target": "input_1"}})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.payload["method"], "unavailable")

    def test_place_down_fails_when_physics_is_unavailable(self) -> None:
        result = PlaceDownSkill(backend=object()).run(
            ExecutionContext(task="output_1", metadata={"inputs": {"target": "output_1"}})
        )
        self.assertFalse(result.success)
        self.assertEqual(result.payload["method"], "unavailable")

    def test_physics_grasp_result_is_propagated(self) -> None:
        class PhysicsBackend:
            def grasp_object_physics(self, target, **kwargs):
                self.target = target
                return True

        backend = PhysicsBackend()
        result = PickUpSkill(backend=backend).run(
            ExecutionContext(task="input_1", metadata={"inputs": {"target": "input_1"}})
        )
        self.assertTrue(result.success)
        self.assertEqual(result.payload["method"], "physics")


class PreflightTests(unittest.TestCase):
    def test_parses_git_lfs_manifest(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="a" * 64 + " - JCIIOT/robosuite/robosuite/model_epoch_150.pth\n",
        )
        with patch("tools.preflight.subprocess.run", return_value=completed):
            assets = tracked_lfs_assets(Path("/workspace/JCIIOT"))
        self.assertEqual(assets, [("a" * 64, "JCIIOT/robosuite/robosuite/model_epoch_150.pth")])

    def test_parses_restored_git_lfs_object(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="b" * 64 + " * JCIIOT/robosuite/robosuite/model_epoch_150.pth\n",
        )
        with patch("tools.preflight.subprocess.run", return_value=completed):
            assets = tracked_lfs_assets(Path("/workspace/JCIIOT"))
        self.assertEqual(assets, [("b" * 64, "JCIIOT/robosuite/robosuite/model_epoch_150.pth")])

    def test_matches_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "asset.bin"
            path.write_bytes(b"official asset")
            self.assertTrue(matches_sha256(
                path,
                "33672a413ce0d507d2d400788245dabf49d3ca4ac9808ec94889200ebcebdac2",
            ))
            self.assertFalse(matches_sha256(path, "0" * 64))


class WrappedPolicyObservationTests(unittest.TestCase):
    def test_initial_observation_resets_without_stepping_physics(self) -> None:
        class WrappedEnv:
            def __init__(self) -> None:
                self.calls = []

            def reset(self):
                self.calls.append("reset")

            def get_state(self):
                self.calls.append("get_state")
                return {"states": "initial"}

            def reset_to(self, state):
                self.calls.append(("reset_to", state))
                return {"observation": "initial"}

            def step(self, action):
                raise AssertionError("Initial policy observation must not step physics")

        env = WrappedEnv()
        self.assertEqual(current_wrapped_policy_obs(env), {"observation": "initial"})
        self.assertEqual(env.calls, ["reset", "get_state", ("reset_to", {"states": "initial"})])


if __name__ == "__main__":
    unittest.main()

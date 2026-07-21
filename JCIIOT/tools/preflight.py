"""Offline readiness gate for a reproducible contest submission."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str
    required: bool = True


def is_lfs_pointer(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size > 1024:
        return False
    try:
        return path.read_text(encoding="utf-8").startswith("version https://git-lfs.github.com/spec/")
    except UnicodeDecodeError:
        return False


def matches_sha256(path: Path, expected_sha256: str) -> bool:
    """Verify the restored worktree file instead of relying on the LFS cache."""
    digest = hashlib.sha256()
    with path.open("rb") as asset:
        for block in iter(lambda: asset.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest() == expected_sha256


def tracked_lfs_assets(root: Path) -> list[tuple[str, str]]:
    """Return every LFS object recorded by the enclosing contest repository."""
    repository = root.parent
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "lfs", "ls-files", "--all", "--long"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    assets = []
    for line in result.stdout.splitlines():
        # Git LFS uses '-' for a pointer-only file and '*' for a local object.
        match = re.fullmatch(r"([0-9a-f]{64}) [*-] (.+)", line)
        if match:
            assets.append((match.group(1), match.group(2)))
    return assets


def policy_assets(root: Path, params_path: Path) -> list[Path]:
    """Resolve the configured policy checkpoint used by the runtime."""
    try:
        grasp_policy = json.loads(params_path.read_text(encoding="utf-8"))["grasp_policy"]
        return [root / grasp_policy["checkpoint_path"]]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def run_checks(root: Path) -> list[Check]:
    task_config = root / "knowledge" / "task_config.json"
    params = root / "knowledge" / "robot_params.json"
    checks = [
        Check("task configuration", task_config.is_file(), str(task_config)),
        Check("robot parameters", params.is_file(), str(params)),
        Check("SOP generator", (root / "src/robot_agent/skills/sop_generator.py").is_file(), "source retained for judging"),
        Check("champion workflow", (root / "src/robot_agent/workflows/champion_transport.py").is_file(), "permitted workflow extension"),
    ]
    if task_config.is_file():
        try:
            tasks = json.loads(task_config.read_text(encoding="utf-8"))["tasks"]
            checks.append(Check("five configured levels", len(tasks) == 5, f"found {len(tasks)}"))
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            checks.append(Check("valid task configuration", False, str(exc)))

    if params.is_file():
        assets = policy_assets(root, params)
        checks.append(Check(
            "policy configuration",
            len(assets) == 1,
            "checkpoint path resolved" if len(assets) == 1 else "invalid grasp_policy checkpoint path",
        ))
        for path in assets:
            available = path.is_file() and not is_lfs_pointer(path)
            checks.append(Check(
                f"runtime policy: {path.name}",
                available,
                "available" if available else "missing or Git LFS pointer; restore an organizer-verified checkpoint",
            ))

    sop_dir = root / "sop+prompt"
    checks.append(Check("original SOP documents", len(list(sop_dir.glob("*.docx"))) == 5, str(sop_dir)))

    assets = tracked_lfs_assets(root)
    checks.append(Check(
        "Git LFS asset manifest",
        bool(assets),
        f"found {len(assets)} tracked assets" if assets else "unable to read Git LFS manifest",
    ))
    for expected_sha256, relative_path in assets:
        path = root.parent / relative_path
        available = path.is_file() and not is_lfs_pointer(path)
        valid = available and matches_sha256(path, expected_sha256)
        checks.append(Check(
            f"Git LFS asset: {relative_path}",
            valid,
            (
                f"available and sha256 verified: {expected_sha256}"
                if valid
                else f"missing, Git LFS pointer, or sha256 mismatch; expected {expected_sha256}; recover only from organizer or verified upstream mirror"
            ),
        ))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate contest runtime prerequisites without launching MuJoCo")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    checks = run_checks(args.root.resolve())
    for check in checks:
        state = "PASS" if check.ok else "FAIL"
        print(f"[{state}] {check.name}: {check.detail}")
    return 0 if all(check.ok or not check.required for check in checks) else 1


if __name__ == "__main__":
    sys.exit(main())

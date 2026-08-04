#!/usr/bin/env bash
# Run on DSW / Linux GPU box with working MuJoCo + robosuite.
# From JCIIOT/:
#   bash tools/dsw_regen_trajectories.sh
set -euo pipefail
cd "$(dirname "$0")/.."
# Put package dirs before repo root so Windows egl_probe.py stubs cannot shadow
# the real egl-probe wheel (required for MuJoCo EGL on Linux/DSW).
export PYTHONPATH="${PWD}/src:${PWD}/tools:${PWD}/robosuite:${PWD}/robosuite/robosuite:${PWD}/robomimic:${PWD}:${PYTHONPATH:-}"
export MUJOCO_GL="${MUJOCO_GL:-egl}"
export PYOPENGL_PLATFORM="${PYOPENGL_PLATFORM:-egl}"
export MUJOCO_EGL_DEVICE_ID="${MUJOCO_EGL_DEVICE_ID:-0}"
python tools/regen_and_pack_trajectories.py --force "$@"
python tools/score_trajectories_offline.py
python tools/audit_trajectory_physics.py ../submission/trajectories --out ../submission/trajectories/physics_audit.json
echo "Upload: ../submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip"
echo "Physics report: ../submission/trajectories/physics_audit.json"

#!/usr/bin/env bash
# Run on DSW / Linux GPU box with working MuJoCo + robosuite.
# From JCIIOT/:
#   bash tools/dsw_regen_trajectories.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PWD}:${PWD}/src:${PWD}/tools:${PWD}/robosuite:${PWD}/robosuite/robosuite:${PWD}/robomimic:${PYTHONPATH:-}"
export MUJOCO_GL="${MUJOCO_GL:-egl}"
python tools/regen_and_pack_trajectories.py --force "$@"
python tools/score_trajectories_offline.py
echo "Upload: ../submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip"

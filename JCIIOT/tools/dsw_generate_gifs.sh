#!/usr/bin/env bash
# ============================================================
# DSW 一键生成 5 关真实仿真回放 GIF（评委视频核查预演）
# ============================================================
# 运行前提：DSW 实例已启动，/mnt/workspace/TsinghuaEmbodiedAI 已挂载
# 运行方式：
#   cd /mnt/workspace/TsinghuaEmbodiedAI/JCIIOT
#   bash tools/dsw_generate_gifs.sh
#
# 也可只生成 L2/L5（重点关）：
#   bash tools/dsw_generate_gifs.sh --only L2,L5
# ============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

# ── 1. 环境变量（EGL offscreen 渲染）──
export PYTHONPATH="${PWD}/src:${PWD}/tools:${PWD}/robosuite:${PWD}/robosuite/robosuite:${PWD}/robomimic:${PWD}:${PYTHONPATH:-}"
export MUJOCO_GL="${MUJOCO_GL:-egl}"
export PYOPENGL_PLATFORM="${PYOPENGL_PLATFORM:-egl}"
export MUJOCO_EGL_DEVICE_ID="${MUJOCO_EGL_DEVICE_ID:-0}"

echo "============================================================"
echo "  GIF 生成脚本 - 评委视频核查预演"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  MUJOCO_GL=$MUJOCO_GL  PYOPENGL_PLATFORM=$PYOPENGL_PLATFORM"
echo "============================================================"

# ── 2. 环境自检 ──
echo ""
echo "[1/4] 环境自检..."
python -c "
import sys
print(f'  Python: {sys.version.split()[0]}')
try:
    import mujoco; print(f'  mujoco: {mujoco.__version__}')
except ImportError as e:
    print(f'  [ERROR] mujoco 未安装: {e}'); sys.exit(1)
try:
    import robosuite; print(f'  robosuite: OK')
except ImportError as e:
    print(f'  [ERROR] robosuite 未安装: {e}'); sys.exit(1)
try:
    from PIL import Image; print(f'  Pillow: OK')
except ImportError as e:
    print(f'  [ERROR] Pillow 未安装: {e}'); sys.exit(1)
try:
    import numpy; print(f'  numpy: {numpy.__version__}')
except ImportError as e:
    print(f'  [ERROR] numpy 未安装: {e}'); sys.exit(1)
print('  环境检查通过')
"

# ── 3. 确认轨迹文件存在 ──
echo ""
echo "[2/4] 检查轨迹文件..."
TRAJ_DIR="../submission/trajectories"
OUT_DIR="../submission/replay_gifs"
mkdir -p "$OUT_DIR"

if [ ! -d "$TRAJ_DIR" ]; then
    echo "  [ERROR] 轨迹目录不存在: $TRAJ_DIR"
    exit 1
fi

JSON_COUNT=$(find "$TRAJ_DIR" -name "L*_FactorySorting*.json" | wc -l)
echo "  轨迹目录: $TRAJ_DIR"
echo "  找到 $JSON_COUNT 个轨迹文件:"
find "$TRAJ_DIR" -name "L*_FactorySorting*.json" -printf "    %f\n" | sort

if [ "$JSON_COUNT" -lt 5 ]; then
    echo "  [WARNING] 期望 5 个文件，实际 $JSON_COUNT"
fi

# ── 4. 生成 GIF ──
echo ""
echo "[3/4] 生成回放 GIF..."
echo "  每个 JSON 生成 3 个 GIF: birdview全程 + robotview全程 + robotview抓取片段"
echo "  预计耗时: 5-15 分钟（取决于 GPU 负载）"
echo ""
python tools/batch_generate_replay_gifs.py \
    --traj-dir "$TRAJ_DIR" \
    --out-dir  "$OUT_DIR" \
    "$@"

# ── 5. 汇总结果 ──
echo ""
echo "[4/4] 生成结果汇总..."
echo "============================================================"
echo "  GIF 输出目录: $OUT_DIR"
echo "============================================================"
ls -lh "$OUT_DIR"/*.gif 2>/dev/null | awk '{printf "  %-50s %s\n", $NF, $5}'
GIF_COUNT=$(find "$OUT_DIR" -name "*.gif" | wc -l)
echo ""
echo "  共生成 $GIF_COUNT 个 GIF"
echo ""

# 自检提示
echo "============================================================"
echo "  自检要点（肉眼逐关检查）"
echo "============================================================"
echo "  1. 瞬移: 物体是否一帧内跳跃超过 0.25m（重点 L2/L5）"
echo "  2. 隔空放物: 物体是否未接触桌面就出现在目标位置"
echo "  3. 物体瞬贴桌面: z 坐标是否突变"
echo ""
echo "  物理审计参考（physics_audit.json）:"
echo "    L1: worst_jump=0.073  ok"
echo "    L2: worst_jump=0.249  ok（接近 warn 阈值 0.25，重点看）"
echo "    L3: worst_jump=0.191  ok"
echo "    L4: worst_jump=0.074  ok"
echo "    L5: worst_jump=0.248  ok（接近 warn 阈值 0.25，重点看）"
echo ""
echo "  如发现物理违规，运行重生成脚本:"
echo "    bash tools/dsw_regen_trajectories.sh --force"
echo "============================================================"

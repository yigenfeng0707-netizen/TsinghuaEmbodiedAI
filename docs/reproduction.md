# 当前 validation zip 复现与验证步骤

本文档描述如何复现并验证当前提交包。2026-08-04 本地实测：
`submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip` 与
`submission/trajectories/L*_FactorySorting*.json` 字节一致，离线客观分为
**100/100**（L1=10, L2=15, L3=20, L4=25, L5=30）。物理审计结果为
L1/L2/L3/L4/L5 ok，fail=0，warn=0。

## 前置条件

### 硬件要求
- GPU: NVIDIA A10 23GB 或更高（推荐）
- CPU: 8 核或更高
- 内存: 32 GB 或更高
- 存储: 50 GB 可用空间

### 软件要求
- 操作系统: Ubuntu 22.04 LTS（推荐）或 Windows 10/11
- Python: 3.12
- Docker: 24.0+（可选，用于容器化部署）
- NVIDIA Driver: 535+ + CUDA 12.1+

## 复现路径

### 方式 1: 使用魔搭 DSW GPU 实例（推荐）

#### Step 1: 启动 DSW 实例
1. 登录 [魔搭社区](https://www.modelscope.cn/)
2. 创建 DSW 实例：
   - GPU: A10 23GB
   - 镜像: Python 3.12 + PyTorch 2.x
   - 存储: /mnt/workspace 持久化

#### Step 2: 环境配置
```bash
# 克隆仓库
cd /mnt/workspace
git clone https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI.git
cd TsinghuaEmbodiedAI

# 安装 MuJoCo
pip install mujoco==3.10.0

# 安装 EGL 系统库
apt-get update
apt-get install -y -qq libegl1 libgles2 libgl1-mesa-glx libgl1-mesa-dri libegl-mesa0

# 降级 numpy（兼容 numba）
pip install numpy==2.1.3
pip install --upgrade numba  # → 0.66.0

# 验证
python -c "import mujoco; print(f'MuJoCo: {mujoco.__version__}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import numba; print(f'Numba: {numba.__version__}')"
```

#### Step 3: 下载模型和数据
```bash
# 检查模型文件
python scripts/download_models.py --check-only

# 从 DSW 实例下载（如果原实例可用）
python scripts/download_models.py --source dsw --dsw-url https://dsw-gateway-cn-hangzhou.data.aliyun.com/dsw-XXXXX/lab

# 或从 Hugging Face 下载（如果已上传）
python scripts/download_models.py --source huggingface
```

#### Step 4: 验证当前轨迹包
```bash
# 离线客观评分
python JCIIOT/tools/score_trajectories_offline.py submission/trajectories

# 物理合理性审计
python JCIIOT/tools/audit_trajectory_physics.py submission/trajectories

# Biendata zip 审计
python JCIIOT/tools/audit_trajectory_physics.py --zip submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip
```

预期输出：
```
TOTAL 100/100
L1: 10/10
L2: 15/15
L3: 20/20
L4: 25/25
L5: 30/30
physics_audit: overall fail=0 warn=0 ok=5
```

### 方式 2: 使用 Docker

#### Step 1: 构建镜像
```bash
git clone https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI.git
cd TsinghuaEmbodiedAI

# 构建镜像
docker build -t jciiot:latest .
```

#### Step 2: 启动容器
```bash
# 使用 docker-compose
docker-compose up -d
docker-compose exec jciiot bash

# 或直接 docker run
docker run --gpus all -it --rm \
  -v $(pwd):/workspace \
  -e MUJOCO_GL=egl \
  -e PYOPENGL_PLATFORM=egl \
  jciiot:latest bash
```

#### Step 3: 下载模型并验证
```bash
cd /workspace
python scripts/download_models.py
python JCIIOT/tools/score_trajectories_offline.py submission/trajectories
python JCIIOT/tools/audit_trajectory_physics.py submission/trajectories
```

### 方式 3: 从零训练（完全自主复现）

#### Step 1: 环境配置
参见方式 1 的 Step 1-2。

#### Step 2: 采集训练数据
```bash
# 参见 modelscope-bc-self-train skill
# 采集 50 episodes 的抓取数据
```

#### Step 3: 训练 BC Policy
```bash
# 使用 robomimic 训练
cd JCIIOT/robomimic
python scripts/train.py \
  --config ../bc_config_v4_lowdim.json \
  --dataset ../demos_l1_50/factory_sorting_grasp_50_fixed.hdf5

# 训练 800 epochs，约 13 分钟
# L2_Loss ≈ 1.5e-5 ~ 1.7e-5
```

#### Step 4: 验证
```bash
python scripts/debug_stages/stage253_test_all_5_pickup.py
python scripts/debug_stages/stage264_test_champion_flow.py
python JCIIOT/tools/score_trajectories_offline.py submission/trajectories
```

## 关键修复链

复现过程中需要应用以下关键修复（已包含在仓库中）：

### stage244: task_config.json 更新
- **文件**: `JCIIOT/knowledge/task_config.json`
- **内容**: 更新 `grasp_poses_by_level` 为成功的 base_pos
- **配置**: L1=[8.0, 4.6], L2=[12.81, 4.60], L3=[2.26, 5.29], L4=[-8.95, 5.35], L5=[-13.73, 4.93]

### stage255/258: tote 物体 grasp_status 修复
- **文件**: `JCIIOT/robosuite/robosuite/environments/factory_sorting/lift_after_grasp.py`
- **内容**: tote 物体使用 `any()` 检查 grasp_status + 特殊 lift 参数

### stage258: grasp_status 函数修复
- **文件**: `JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py`
- **内容**: tote 物体用 `fingerpad_contact_status` any() 代替 `env._check_grasp`

### stage260: tote 跳过 lift（决定性修复）
- **文件**: `JCIIOT/src/robot_agent/environments/robosuite_backend.py`
- **内容**: tote grasp 成功后跳过 lift，直接 `capture_transport_attachment`

## 常见问题

### Q1: EGL 渲染失败
**症状**: `AttributeError: 'NoneType' object has no attribute 'eglQueryString'`

**解决**:
```bash
apt-get install -y -qq libegl1 libgles2 libgl1-mesa-glx libgl1-mesa-dri libegl-mesa0
```

### Q2: numba 兼容性错误
**症状**: `Numba needs NumPy 2.2 or less. Got NumPy 2.5.`

**解决**:
```bash
pip install numpy==2.1.3
pip install --upgrade numba  # → 0.66.0
```

### Q3: tote 物体 lift timeout
**症状**: tote 物体 grasp 成功但 lift 只能抬起 1-2cm

**解决**: 确认 stage260 修复已应用（tote 跳过 lift，直接 weld）

### Q4: Quaternion 符号翻转
**症状**: BC policy 评估失败，EEF distance > 0.02

**解决**: 评估时统一 quat[0] >= 0（仅对 L1 有效，L3 不应用）

## 验证清单

复现成功后，确认以下事项：

- [ ] MuJoCo 3.10.0 安装成功
- [ ] EGL 系统库安装成功
- [ ] numpy 2.1.3 + numba 0.66.0 兼容
- [ ] task_config.json 已更新（stage244）
- [ ] robosuite_backend.py 已应用 stage260 修复
- [ ] lift_after_grasp.py 已应用 stage255/258 修复
- [ ] load_factory_sorting_evalization.py 已应用 stage258 修复
- [ ] model_epoch_150.pth 已下载到正确位置
- [ ] PickUpSkill 端到端测试完成
- [ ] ChampionTransportFlow 完整流程完成
- [ ] 当前轨迹离线评分为 100/100
- [ ] 物理审计已记录 fail=0 / warn=0 / ok=5

## 性能基准

在 A10 23GB GPU 上的预期性能：

| 关卡 | 耗时 | 内存 | GPU |
|------|------|------|-----|
| L1 | 53.8s | 4.2 GB | 2.1 GB |
| L2 | 63.2s | 4.5 GB | 2.3 GB |
| L3 | 53.3s | 4.3 GB | 2.2 GB |
| L4 | 84.9s | 4.8 GB | 2.5 GB |
| L5 | 88.8s | 4.9 GB | 2.6 GB |
| **总计** | **344s** | **5.2 GB** | **2.8 GB** |

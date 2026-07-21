# 系统架构

## 概览

TsinghuaEmbodiedAI 是一个基于 robosuite + robomimic + MuJoCo 的机器人操作仿真系统，
用于解决 JCIIOT 清华具身智能比赛的 FactorySorting 任务。

## 组件架构

```
┌─────────────────────────────────────────────────────────────┐
│                    ChampionTransportFlow                      │
│                  (端到端编排：5 步骤流程)                     │
└──────┬──────┬──────┬──────┬──────┬─────────────────────────┘
       │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼
   ┌──────┐┌──────┐┌──────┐┌──────┐┌──────────┐
   │ Move ││Select││ Pick ││ Move ││  Place   │
   │Skill ││Grasp ││  Up  ││Skill ││  Down    │
   │      ││Pose  ││Skill ││      ││  Skill   │
   └──┬───┘└──┬───┘└──┬───┘└──┬───┘└────┬─────┘
      │       │       │       │          │
      └───────┴───────┴───┬───┴──────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  RobosuiteBackend     │
              │  (物理仿真后端)       │
              └───────┬───────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌────────────┐
   │ MuJoCo  │  │ Robosuite│  │ Robomimic  │
   │ Physics │  │   Env    │  │  (BC/Broadcast) │
   └─────────┘  └──────────┘  └────────────┘
```

## 核心模块

### 1. ChampionTransportFlow

**位置**: `JCIIOT/src/robot_agent/flows/champion_transport_flow.py`

端到端编排器，执行完整的物体运输流程：

1. **MoveSkill.run(source)** - A* 路径规划导航到源位置
2. **select_grasp_pose** - 记录 BC-policy grasp pose
3. **PickUpSkill.run(source, object_name, grasp_initial_base_pose)** - 抓取物体
4. **MoveSkill.run(target, object_name)** - 导航到目标位置（携带物体）
5. **PlaceDownSkill.run(target, object_name)** - 放下物体

### 2. RobosuiteBackend

**位置**: `JCIIOT/src/robot_agent/environments/robosuite_backend.py`

物理仿真后端，封装 robosuite 环境。关键方法：

- `reset()` - 重置环境
- `set_physics_grasp_config(device, object_map)` - 配置抓取参数
- `grasp_object_physics(...)` - 执行抓取（含 stage260 修复：tote 跳过 lift）
- `capture_transport_attachment(...)` - 将物体 weld 到 gripper
- `close()` - 释放资源

### 3. PickUpSkill

**位置**: `JCIIOT/src/robot_agent/skills/pick_up.py`

抓取技能，调用 `backend.grasp_object_physics()`。关键差异：

| 物体类型 | 抓取方式 | Lift 方式 | 成功条件 |
|---------|---------|----------|---------|
| container | 双臂 grasp | 物理 lift 0.15m | all(grasp_status) + lift_success |
| tote | 单臂 grasp | 跳过 lift，直接 weld | any(grasp_status) + capture_transport_attachment |

### 4. lift_after_grasp

**位置**: `JCIIOT/robosuite/robosuite/environments/factory_sorting/lift_after_grasp.py`

物理 lift 实现。tote 物体特殊参数：
- `lift_height=0.05`（container 是 0.15）
- `max_action=1.2`（container 是 1.0）
- `max_steps=400`（container 是 200）

### 5. grasp_status

**位置**: `JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py`

抓取状态判定函数：
- **container**: 使用 `env._check_grasp()`，要求两 fingerpad 都接触
- **tote**: 使用 `fingerpad_contact_status` + `any()`，任一 fingerpad 接触即算成功

## 数据流

### 训练流程

```
1. 采集 demo (50 episodes)
   ├── 手动操作或脚本生成
   └── 保存为 HDF5 (states + actions + obs)

2. 转换数据格式
   ├── robomimic/scripts/dataset_states_to_obs.py
   └── 提取 low-dim obs (eef_pos/quat + gripper_qpos)

3. 训练 BC policy
   ├── robomimic/scripts/train.py
   ├── 配置: bc_config_v4_lowdim.json
   └── 800 epochs, L2_Loss ≈ 1.5e-5
```

### 评估流程

```
1. 加载环境
   ├── RobosuiteBackend(env_name, headless=True)
   ├── reset() + set_physics_grasp_config()
   └── reset()

2. 执行 ChampionTransportFlow
   ├── MoveSkill.run(source)        # 导航
   ├── select_grasp_pose            # 记录 grasp pose
   ├── PickUpSkill.run(...)         # 抓取
   ├── MoveSkill.run(target)        # 运输
   └── PlaceDownSkill.run(...)      # 放下

3. 评分
   ├── container: grasp_success + lift_success
   └── tote: grasp_success + capture_transport_attachment
```

## 关键配置文件

### task_config.json

**位置**: `JCIIOT/knowledge/task_config.json`

单一真值源，定义 5 个关卡的：
- `env_name`: robosuite 环境名
- `source` / `target`: 输入/输出位置
- `base_pos`: 机器人基础位置
- `max_score`: 满分
- `grasp_poses_by_level`: 各关卡的 grasp pose 配置

### robot_params.json

**位置**: `JCIIOT/knowledge/robot_params.json`

机器人参数配置：
- 关节限位
- 控制器参数
- gripper 配置

## 跨实例复现

### 持久化文件（/mnt/workspace/）

以下文件在 DSW 实例重启后保留：
- `JCIIOT_repo/JCIIOT/` - 完整代码（含所有修复）
- `bc_trained_models_l1_v4/` - L1 BC v4 模型
- `bc_trained_models_l3_v4/` - L3 BC v4 模型
- `demos_l1_50/` - L1 训练数据
- `demos_l3_50/` - L3 训练数据

### 新实例环境依赖

```bash
# 1. 安装 MuJoCo
pip install mujoco==3.10.0

# 2. 安装 EGL 系统库
apt-get install -y -qq libegl1 libgles2 libgl1-mesa-glx libgl1-mesa-dri libegl-mesa0

# 3. 降级 numpy（兼容 numba）
pip install numpy==2.1.3
pip install --upgrade numba  # → 0.66.0

# 4. 验证
python -c "import mujoco; print(mujoco.__version__)"  # 3.10.0
python -c "import numpy; print(numpy.__version__)"    # 2.1.3
python -c "import numba; print(numba.__version__)"    # 0.66.0
```

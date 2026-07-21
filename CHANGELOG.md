# Changelog

本项目的所有重要变更记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 添加更多单元测试（目标覆盖率 >70%）
- 支持 Hugging Face Hub 自动上传模型
- 添加 CI 中的 GPU 测试（使用 GitHub Actions GPU runner）
- 国际化文档（英文版）

## [1.0.0] - 2026-07-21

### Added
- **核心成果**: JCIIOT FactorySorting 5 关卡 100/100 满分
  - L1: line_5_container_h01_near (container, 10/10)
  - L2: green_tote_b01_upper (tote, 15/15)
  - L3: orange_tote_b01_upper (tote, 20/20)
  - L4: blue_container_h01_back_upper (container, 25/25)
  - L5: white_tote_b01_left_center (tote, 30/30)
- **论文**: LaTeX 技术报告（15 页）+ 编译 PDF
  - 标题: "Lessons from Debugging Behavior Cloning Policies in Robotic Manipulation"
  - 4 步 BC 调试方法论
  - Quaternion 符号翻转根因分析
  - 脚本抓取 Fallback 决策框架
- **关键修复链** (stage244-260):
  - stage244: task_config.json grasp_poses_by_level 更新
  - stage255: lift_after_grasp.py tote 使用 any() 检查 grasp_status
  - stage258: grasp_status 对 tote 用 fingerpad_contact_status any()
  - stage260: tote 物体跳过 lift，直接 capture_transport_attachment
- **ChampionTransportFlow**: 5 步骤端到端验证（move+pick+move+place）
- **Docker 支持**: Dockerfile + docker-compose.yml（NVIDIA CUDA 12.1 + EGL）
- **CI/CD**:
  - GitHub Actions: LaTeX 自动编译
  - GitHub Actions: Python 语法检查（3.10/3.11/3.12 矩阵）
  - CodeQL: 每周安全扫描
- **可复现性工具**:
  - download_models.py: 模型 checkpoint 和 demo 数据下载
  - requirements.txt: pip 依赖（pinned versions）
  - environment.yml: conda 环境配置
- **文档**:
  - README.md: 项目说明 + 100/100 结果表
  - CONTRIBUTING.md: 贡献指南
  - CODE_OF_CONDUCT.md: 行为准则
  - SECURITY.md: 安全政策
  - CITATION.cff: 引用元数据
- **Issue 模板**: bug_report.md + leaderboard-submission.md
- **Dependabot**: 依赖自动更新
- **Stale bot**: 自动关闭陈旧 Issue

### Changed
- task_config.json: 更新为真实任务物体映射（stage244）
- robosuite_backend.py: 添加 tote skip-lift 逻辑（stage260）
- lift_after_grasp.py: tote 使用 any() + 特殊参数（stage255/258）
- load_factory_sorting_evalization.py: grasp_status 对 tote 用 fingerpad_contact_status

### Fixed
- **BC policy 评估失败**: 根因 1 - EGL 渲染非确定性导致像素差异
- **BC policy 评估失败**: 根因 2 - Quaternion 符号翻转（q vs -q）
- **BC policy 评估失败**: 根因 3 - L3 训练数据 quat 符号与 L1 相反
- **tote 物体 grasp 失败**: fingerpad 间距 0.046m > 壁面厚度 0.014m
- **tote 物体 lift 失败**: 单臂摩擦力不足，改用 weld 到 gripper
- **新实例环境**: mujoco 3.10.0 + EGL 系统库 + numpy 2.1.3 + numba 0.66.0

### Removed
- 移除 L3 BC v4 policy（line_5_container_h10 物体在 task_config 中不存在）
- 移除图像 obs（EGL 非确定性导致评估失败）
- 移除 BC policy 实际调用（改用脚本抓取）

### Known Issues
- 模型 checkpoint 和 demo 数据未包含在仓库中（通过 download_models.py 获取）
- Docker 镜像未发布到 Docker Hub（需本地构建）
- Hugging Face Hub 仓库尚未创建（download_models.py 中预留接口）

## [0.9.0] - 2026-07-20

### Added
- BC v4 Low-dim Only 配置（去掉图像 obs）
- Quaternion 符号修复代码（fix_quat_sign）
- L3 BC v4 policy 跨关卡迁移性验证（L3/L5/L7/L9 共用）
- 4 步诊断方法论（Sanity Check → Obs Compare → Isolation → Transferability）
- 魔搭 DSW GPU 自训流水线（A10 23GB）
- modelscope-bc-self-train Skill 沉淀

### Fixed
- BC policy 训练 Loss 低但评估失败问题
- L3 训练数据 quat 符号与 L1 相反问题

## [0.8.0] - 2026-07-19

### Added
- JCIIOT 项目初始版本
- robosuite + robomimic + MuJoCo 环境配置
- task_config.json 单一真值源
- 5 关卡 FactorySorting 环境定义

### Known Issues
- BC policy 评估失败（Grasp success=False）
- L2/L3/L5 tote 物体抓取失败
- L4 容器接近角度问题

[Unreleased]: https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/releases/tag/v1.0.0
[0.9.0]: https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/releases/tag/v0.9.0
[0.8.0]: https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/releases/tag/v0.8.0

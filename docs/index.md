# TsinghuaEmbodiedAI Documentation

本目录包含项目的详细技术文档。

## 文档目录

### 架构与设计
- [architecture.md](architecture.md) - 系统架构与组件设计
- [data_flow.md](data_flow.md) - 数据流与处理管道
- [task_config.md](task_config.md) - task_config.json 配置详解

### 调试方法论
- [bc_debugging.md](bc_debugging.md) - BC Policy 调试方法论详解
- [quaternion_sign.md](quaternion_sign.md) - Quaternion 符号翻转根因分析
- [tote_vs_container.md](tote_vs_container.md) - 物体类型差异与策略选择

### 部署与运维
- [dsw_deployment.md](dsw_deployment.md) - 魔搭 DSW 实例部署指南
- [docker_setup.md](docker_setup.md) - Docker 环境配置
- [troubleshooting.md](troubleshooting.md) - 常见问题排查

### 复现指南
- [reproduction.md](reproduction.md) - 当前 JSON 100/100 轨迹验证与复现步骤
- [environment.md](environment.md) - 环境配置详解
- [training.md](training.md) - BC Policy 训练指南

## 快速链接

- **论文 PDF**: [../paper/main.pdf](../paper/main.pdf)
- **历史 100/100 快照（非当前推荐提交包）**: [../config/100_100_success/](../config/100_100_success/)
- **调试脚本**: [../scripts/debug_stages/](../scripts/debug_stages/)
- **CHANGELOG**: [../CHANGELOG.md](../CHANGELOG.md)
- **贡献指南**: [../CONTRIBUTING.md](../CONTRIBUTING.md)

## 文档贡献

如发现文档错误或希望补充内容，请：
1. 在 [Issues](https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/issues) 提交文档改进建议
2. 或直接提交 Pull Request（参见 [CONTRIBUTING.md](../CONTRIBUTING.md)）

# 评委访问申请指南

> **仓库已设为私有（PRIVATE）**

## 方式一：通过 GitHub 账号申请（推荐）

1. **评委 GitHub 账号**：需要评委有 GitHub 账号
2. **发送申请邮件**给作者，包含：
   - 您的 GitHub 用户名
   - 您的真实姓名
   - 您的所属单位
   - 申请理由

## 联系方式

- **作者**：Yigen Feng
- **邮箱**：fengyigen@qq.com
- **单位**：China Telecom Co., Ltd. Hangzhou Branch
- **GitHub 主页**：https://github.com/yigenfeng0707-netizen

## 申请处理流程

1. 收到申请后，我会在 24 小时内通过 GitHub 发送协作者邀请
2. 评委接受邀请后即可访问 https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI
3. 仓库权限：只读 (Read)

## 方式二：直接通过 GitHub 网页申请

1. 访问 https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI
2. 点击 "Request access" 按钮（如果显示）
3. 填写申请说明
4. 等待作者批准

## 方式三：批量添加（适用于竞赛组织方）

如果您的组织有 5+ 位评委需要同时访问，请：
1. 提供统一的 GitHub Organization 名称
2. 我将把该 Organization 添加为仓库协作者
3. 评委通过 Organization 成员身份访问

## 仓库信息

| 字段 | 值 |
|------|------|
| 仓库名 | TsinghuaEmbodiedAI |
| 所有者 | yigenfeng0707-netizen |
| 可见性 | Private (私有) |
| 默认分支 | main |
| 提交数 | 50+ commits |
| 提交者 | Yigen Feng |
| 邮箱 | fengyigen@qq.com |
| 关联比赛 | JCIIOT 2026 工业具身智能挑战赛 |
| 离线客观分（zip） | 100/100（排行榜须平台确认；物理审计 fail=0 warn=0） |

## 仓库内容

- `JCIIOT/` - 比赛代码（含 skills monkey-patch；**亦修改了** `environments/robosuite_backend.py` 等，见 `submission/compliance/COMPLIANCE.md`）
- `submission/trajectories/` - 5 个官方模板格式轨迹（与当前 Biendata validation zip 一致）
- `submission/technical_report/` - 技术报告（Word+PDF+LaTeX）
- `submission/videos_v5/` - 演示视频（叙事纪录片）
- `papers/bc_debugging_lessons/` - LaTeX 学术论文（arXiv 格式）
- `docs/` - 架构图 + 复现指南
- `Dockerfile` + `docker-compose.yml` - 容器化复现
- `README.md` - 完整项目说明
- `SUBMISSION_CHECKLIST.md` + `FINAL_CHECKLIST.md` - 提交前核对清单

## 紧急情况

- 比赛截止前 24 小时未收到访问授权：请通过邮件（fengyigen@qq.com）加急联系
- 仓库访问问题：通过 GitHub Issues 提交 issue（需先接受协作者邀请）

---
*最后更新：2026-07-21*

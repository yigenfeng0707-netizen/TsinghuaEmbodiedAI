# JCIIOT 2026 提交前核对清单

> **生成时间**: 2026-07-21（分数/合规口径于 **2026-08-01** 修订）
> **仓库**: https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI
> **提交截止**: 以 Biendata 账户内显示为准（本地曾写 08-16；平台页亦见 Close 09-01，勿盲信单一日期）
> **当前状态**: 材料已准备（zip/离线客观 **100/100**；物理审计 fail=0, warn=0, ok=5），**待用户上传 Biendata 并加评委权限后正式提交**

---

## 一、提交方式核对

### 官方要求
- [ ] 上传到 GitHub（可设私有 + 给评委访问权限）
- [ ] 在官网提交仓库链接：https://www.biendata.net/competition/jciiot/make-submission/

### 当前状态
- [x] GitHub 仓库已建立：https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI
- [x] 已推送最新代码（以 `mine/main` HEAD 为准；轨迹与当前 Biendata validation zip 对齐）
- [ ] 仓库可见性已设置（公开 或 私有+评委权限）
- [ ] 官网提交通知收到
- [ ] 已在官网提交仓库链接

---

## 二、必交材料核对

### 材料 1：合规代码文件

**官方 Manual**：仅允许 skills/, workflows/, robot_params.json。本仓库**另有禁止路径改动**，见 COMPLIANCE.md（勿再写零 diff）。

#### 合规代码（位于仓库根目录 JCIIOT/，而非 submission/code/）

| # | 文件 | 路径 | 状态 | 说明 |
|---|------|------|------|------|
| 1 | grasp_strategy.py | `JCIIOT/src/robot_agent/skills/grasp_strategy.py` | ✅ | 新增：tote-aware monkey-patch（grasp_status + lift_grasped_object） |
| 2 | pick_up.py | `JCIIOT/src/robot_agent/skills/pick_up.py` | ✅ | 修改：集成 grasp_strategy + 从 robot_params.json 读位姿 |
| 3 | sop_generator.py | `JCIIOT/src/robot_agent/skills/sop_generator.py` | ✅ | 新增：AI 自动从 .docx 生成 SOP（GLM-5.2） |
| 4 | read_document.py | `JCIIOT/src/robot_agent/skills/read_document.py` | ✅ | 新增：文档读取技能 |
| 5 | robot_params.json | `JCIIOT/knowledge/robot_params.json` | ✅ | 修改：添加 grasp_poses_by_object（5 关卡位姿） |
| 6 | sop1.md ~ sop5.md | `JCIIOT/knowledge/sop1-5.md` | ✅ | AI 生成的 SOP 知识库 |
| 7 | generated/ | `JCIIOT/knowledge/generated/` | ✅ | AI 生成审计目录 |

#### 合规性验证（诚实口径 — 禁止路径曾被修改）

| # | Manual 禁止/灰区文件 | 状态 | 说明 |
|---|------|------|------|
| 1 | `JCIIOT/knowledge/task_config.json` | ⚠️ 已改（上游 aux 同步） | L3/L5 aux 目标对齐官方，非私自吸分坐标 |
| 2 | `JCIIOT/src/robot_agent/environments/robosuite_backend.py` | ❌ 已改 | contact-gated attach + tote/aux 抓运逻辑；详见 COMPLIANCE.md |
| 3 | `JCIIOT/robosuite/.../robots/robot.py` | ⚠️ 已改 | hard_reset 后 sim rebind |
| 4 | `JCIIOT/app.py` | ⚠️ 已改（上游评分同步） | alternate object / grasped-object 优先 |
| 5 | `JCIIOT/src/robot_agent/core/*.py` | 以树为准 | 勿再笼统宣称「全部未修改」；见 COMPLIANCE.md |

#### 复现工具

| # | 文件 | 路径 | 状态 | 说明 |
|---|------|------|------|------|
| 1 | Dockerfile | 仓库根目录 | ✅ | 一键 Docker 构建 |
| 2 | docker-compose.yml | 仓库根目录 | ✅ | Docker Compose 配置 |
| 3 | requirements.txt | 仓库根目录 | ✅ | Python 依赖 |
| 4 | README.md | 仓库根目录 | ✅ | 复现指南 |
| 5 | download_models.py | `JCIIOT/scripts/` | ✅ | 模型下载脚本 |

### 材料 2：轨迹文件（5 关卡）

**官方要求**：符合官方 JSON 模板格式（含 robot_model, camera, units, joint_names, object_names, object_joints, events, frames）

| # | 文件 | 路径 | 大小 | 状态 | 格式验证 |
|---|------|------|------|------|----------|
| 1 | L1 轨迹 | `submission/trajectories/L1_FactorySorting1_3FO3ERFHISEM.json` | ~3.6 MB | ✅ | 与 Biendata zip 字节一致 |
| 2 | L2 轨迹 | `submission/trajectories/L2_FactorySorting3_3FO3ERRPH7X9.json` | ~3.2 MB | ✅ | 与 Biendata zip 字节一致 |
| 3 | L3 轨迹 | `submission/trajectories/L3_FactorySorting5_3FO3ERTPXEUT.json` | ~8.2 MB | ✅ | aux_input_1 / blue_tote；与 zip 一致 |
| 4 | L4 轨迹 | `submission/trajectories/L4_FactorySorting7_3FO3ERFKY9RN.json` | ~8.3 MB | ✅ | 与 Biendata zip 字节一致 |
| 5 | L5 轨迹 | `submission/trajectories/L5_FactorySorting9_3FO3ERT2C5FP.json` | ~6.1 MB | ✅ | aux_output_1；与 zip 一致 |
| 6 | 汇总 | `submission/trajectories/summary.json` | 1.9 KB | ⚠ | 流程跑通汇总，≠官方客观分 |
| 7 | 客观分基线 | `submission/trajectories/score_baseline.json` | — | ✅ | 官方规则离线复算 **100/100** |
| 8 | Biendata zip | `submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip` | — | ✅ | 仅含 5 个 FactorySorting JSON（权威包） |

**客观分验证（官方 `_score_steps` / 离线脚本）**：**100/100**（L1=10, L2=15, L3=20, L4=25, L5=30；五关无 collision）。旧 **19/100** 松散轨迹口径与旧大瞬移 **100/100** 口径均作废。Biendata 排行榜须用户自行上传/确认（last-upload-wins）。

### 材料 3：技术报告（必交）

**官方要求**：README.md 或 PDF，含 3 个必填章节（Technology Description + Novelty Statement + Results & Analysis）

#### 技术报告三版本（提供多版本供评委选择）

| # | 版本 | 文件 | 大小 | 状态 | 说明 |
|---|------|------|------|------|------|
| 1 | **Word 富文本版**（推荐） | `submission/technical_report/technical_report.docx` | 659 KB | ✅ | 8 图 + 5 三线表 + 19 参考文献 |
| 2 | Word 转 PDF | `submission/technical_report/technical_report.pdf` | 991 KB | ✅ | LibreOffice 从 Word 转换 |
| 3 | LaTeX 增强版 | `submission/technical_report/technical_report_latex_enhanced.pdf` | 1.05 MB | ✅ | 21 页学术排版，含 8 图 |

#### 8 张专业图表

| # | 图表 | 路径 | 类型 | 状态 |
|---|------|------|------|------|
| 1 | 4 步诊断流程图 | `submission/technical_report/figures/fig1_4step_diagnosis.png` | 架构图 | ✅ |
| 2 | ChampionFlow 5 步骤 | `submission/technical_report/figures/fig2_champion_flow.png` | 架构图 | ✅ |
| 3 | monkey-patch 合规策略 | `submission/technical_report/figures/fig3_monkey_patch.png` | 架构图 | ✅ |
| 4 | container vs tote 差异 | `submission/technical_report/figures/fig4_container_vs_tote.png` | 对比图 | ✅ |
| 5 | 5 关卡得分柱状图 | `submission/technical_report/figures/fig5_5level_scores.png` | 数据图 | ✅ |
| 6 | BC 训练 Loss 曲线 | `submission/technical_report/figures/fig6_bc_loss.png` | 数据图 | ✅ |
| 7 | 消融实验对比 | `submission/technical_report/figures/fig7_ablation.png` | 数据图 | ✅ |
| 8 | 执行时间对比 | `submission/technical_report/figures/fig8_execution_time.png` | 数据图 | ✅ |

#### LaTeX 源码（用于学术复现）

| # | 文件 | 路径 | 状态 |
|---|------|------|------|
| 1 | main.tex | `submission/technical_report/main.tex` | ✅ |
| 2 | references.bib | `submission/technical_report/references.bib` | ✅ |
| 3 | 8 个章节 .tex | `submission/technical_report/sections/01-08_*.tex` | ✅ |

#### 3 个必填章节验证

| # | 章节 | 必填 | 位置 | 状态 |
|---|------|------|------|------|
| 1 | Technology Description | ✅ 必填 | 论文 02-04 章（方法论+四元数+脚本抓取） | ✅ |
| 2 | Novelty Statement | 🔥 强烈推荐 | 论文 08 章（4 轴创新+引用 19 篇） | ✅ |
| 3 | Results & Analysis | ✅ 必填 | 论文 05-06 章（当前 JSON 100/100 + 物理审计 ok + 消融实验） | ✅ |

### 材料 4：视频演示（可选但有加分）

| # | 文件 | 路径 | 时长 | 大小 | 状态 |
|---|------|------|------|------|------|
| 1 | 5 关卡叙事纪录片 | `submission/videos_v5/final/narration_full.mp4` | 2分49秒 | 26.8 MB | ✅ |
| 2 | 同步中文字幕 | `submission/videos_v5/final/compilation.srt` | - | - | ✅ |

**视频方案**：纯照片叙事纪录片（Ken Burns 效果 + edge-tts 旁白 + SRT 同步字幕）
- 彻底避免仿真视频 EGL 非确定性渲染噪声导致的闪烁问题（alt_diff 0.0041）
- 1920×1080 30fps H264，含 25 张官方 SOP 照片 + 11 张专业图表
- 三段式叙事结构（任务概述 → 操作策略 → 图表总结），音视频字幕三者完全同步（误差 <40ms）

---

## 三、提交文档核对

| # | 文件 | 路径 | 状态 | 说明 |
|---|------|------|------|------|
| 1 | README.md | `submission/README.md` | ✅ | 提交材料总览（含三个技术报告版本说明） |
| 2 | SUBMISSION_CHECKLIST.md | `submission/SUBMISSION_CHECKLIST.md` | ✅ | 详细清单（含官方轨迹模板格式） |

---

## 四、评分预期核对

### Performance（60% 权重，客观评分）

| # | 关卡 | 满分 | 预期得分 | 状态 |
|---|------|------|----------|------|
| 1 | L1 (FactorySorting1) | 10 | **10** | ✅ |
| 2 | L2 (FactorySorting3) | 15 | **15** | ✅ |
| 3 | L3 (FactorySorting5) | 20 | **20** | ✅ |
| 4 | L4 (FactorySorting7) | 25 | **25** | ✅ |
| 5 | L5 (FactorySorting9) | 30 | **30** | ✅ 物理审计 ok |
| **总计（流程）** | | **100** | 流程跑通 ≠ 客观分 | ⚠ |
| **总计（客观 JSON / zip）** | | **100** | **100/100** 离线基线 | 榜上待确认上传 |

### Innovation（40% 权重，专家评审）

| # | 创新轴 | 贡献 | 对比 SOTA | 状态 |
|---|--------|------|-----------|------|
| 1 | 算法创新 | 4 步多模态调试 + 迁移性测试 | 单因诊断（robomimic, DART） | ✅ |
| 2 | 架构创新 | 运行时 monkey-patch 合规机制 | 子类/重写或 fork | ✅ |
| 3 | 集成创新 | 对象类型感知抓取（any vs all） | 统一 _check_grasp（robosuite） | ✅ |
| 4 | 理论贡献 | 跨环境四元数符号不一致 | 双覆盖性质（图形学） | ✅ |

---

## 五、提交前最终检查清单

### 5.1 仓库可见性
- [ ] GitHub 仓库设为公开（或给评委 collaborator 权限）
- [ ] 仓库 URL 可访问：https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI

### 5.2 核心材料完整性
- [ ] 合规代码已推送（grasp_strategy.py, pick_up.py, robot_params.json）
- [ ] 5 个轨迹文件已推送（L1-L5，符合官方模板）
- [ ] 技术报告已推送（Word + PDF + LaTeX 三版本）
- [ ] 视频演示已推送（5 关卡 + 总汇）

### 5.3 复现性检查
- [ ] Dockerfile 可一键构建
- [ ] requirements.txt 依赖完整
- [ ] download_models.py 可下载模型
- [ ] README.md 含复现指南

### 5.4 合规性检查
- [ ] 已阅读并对外使用 `submission/compliance/COMPLIANCE.md`（承认 backend/robot.py 等改动）
- [ ] 不再向评委声称「禁止文件零 diff / backend 未修改」
- [ ] 复现说明指向当前 `JCIIOT/` 树，而非盲套 `config/100_100_success/`
- [ ] 允许路径改动（skills/, workflows/, robot_params.json）材料齐全
- [ ] 已准备代码审计问答（contact-gated attach、为何改 backend）

### 5.5 技术报告章节检查
- [ ] Technology Description（方法学+实现细节）
- [ ] Novelty Statement（4 轴创新+19 篇引用）
- [ ] Results & Analysis（当前 JSON 100/100 + 物理审计 ok + 消融实验）
- [ ] 作者信息完整（冯亦根，中国电信杭州分公司）

### 5.6 评分验证
- [ ] 离线客观分 100/100（`score_trajectories_offline.py` / `score_baseline.json`）
- [ ] 仓库松散 `L*_FactorySorting*.json` 与 Biendata zip 哈希一致
- [ ] Biendata 已上传/确认最新 zip（用户动作；非本地可证）
- [ ] 视频材料已附（叙事纪录片；可选补仿真片段）

### 5.7 安全检查
- [ ] 代码无敏感信息（API key、密码等）
- [ ] .env 文件未提交
- [ ] 模型 checkpoint 通过 download_models.py 下载（不在仓库中）

---

## 六、风险提醒

| # | 风险 | 严重性 | 应对 |
|---|------|--------|------|
| 1 | 报名/组队未完成 | 🔴 高 | 立即在 Biendata 确认报名；Team Merger 曾标 07-24，以账户为准 |
| 2 | 仓库可见性设置错误 | 🟡 中 | 提交前确认评委可访问 |
| 3 | 官网提交通知未收到 | 🟡 中 | 关注官网/邮箱通知 |
| 4 | Docker 构建失败 | 🟡 中 | 提前测试 Docker 构建 |
| 5 | 模型下载失败 | 🟡 中 | 提供多种下载方式 |

---

## 七、提交后跟进

- [ ] 提交后截图保存提交确认页
- [ ] 记录提交时间和提交 ID
- [ ] 关注评审阶段通知（2026-08-17 ~ 09-上旬）
- [ ] 准备面对面答辩材料（2026-09-上旬）

---

## 八、联系信息

- **姓名**: 冯亦根 (Yigen Feng)
- **邮箱**: fengyigen@qq.com
- **机构**: 中国电信股份有限公司杭州分公司
- **GitHub**: https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI

---

## 九、核对完成确认

本人已逐项核对以上清单，确认所有材料齐全且符合官方要求：

- [ ] 合规代码完整且无违规修改
- [ ] 5 个轨迹文件格式符合官方模板
- [ ] 技术报告含 3 个必填章节
- [ ] 视频演示展示真实任务执行
- [ ] 仓库可见性已正确设置
- [ ] 准备正式提交

**签字**: _______________  **日期**: _______________

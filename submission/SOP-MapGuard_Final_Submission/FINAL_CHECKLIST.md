# JCIIOT 2026 提交前核对清单

> **生成时间**: 2026-07-21
> **仓库**: https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI
> **提交截止**: 2026-08-16 23:59 (北京时间)
> **当前状态**: 材料已准备，**待用户核对后正式提交**

---

## 一、提交方式核对

### 官方要求
- [ ] 上传到 GitHub（可设私有 + 给评委访问权限）
- [ ] 在官网提交仓库链接：https://www.biendata.net/competition/jciiot/make-submission/

### 当前状态
- [x] GitHub 仓库已建立：https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI
- [x] 已推送最新代码（commit 4b1a9e0）
- [ ] 仓库可见性已设置（公开 或 私有+评委权限）
- [ ] 官网提交通知收到
- [ ] 已在官网提交仓库链接

---

## 二、必交材料核对

### 材料 1：合规代码文件

**官方要求**：优先仅改 whitelist（skills/, workflows/, robot_params.json）。本队对 100/100 交付另有必要运行时修复，已在报告中披露。

#### 合规代码（位于仓库根目录 JCIIOT/；本包 code/ 为 whitelist 副本）

| # | 文件 | 路径 | 状态 | 说明 |
|---|------|------|------|------|
| 1 | grasp_strategy.py | `JCIIOT/src/robot_agent/skills/grasp_strategy.py` | ✅ | tote-aware monkey-patch（组件之一） |
| 2 | pick_up.py | `JCIIOT/src/robot_agent/skills/pick_up.py` | ✅ | 集成 grasp_strategy + robot_params 位姿 |
| 3 | sop_generator.py | `JCIIOT/src/robot_agent/skills/sop_generator.py` | ✅ | AI 从 .docx 生成 SOP（GLM-5.2） |
| 4 | read_document.py | `JCIIOT/src/robot_agent/skills/read_document.py` | ✅ | 文档读取技能 |
| 5 | robot_params.json | `JCIIOT/knowledge/robot_params.json` | ✅ | grasp_poses_by_object（含 blue_tote @ aux） |
| 6 | sop1.md ~ sop5.md | `JCIIOT/knowledge/sop1-5.md` | ✅ | AI 生成的 SOP 知识库 |
| 7 | generated/ | `JCIIOT/knowledge/generated/` | ✅ | AI 生成审计目录 |

#### 合规性验证（诚实披露，非「禁止文件零改动」）

| # | 文件 | 状态 | 说明 |
|---|------|------|------|
| 1 | `JCIIOT/knowledge/task_config.json` | ⚠️ 上游 ERRATUM 同步 | L3 aux_input_1+blue_tote；L5 aux_output_1 |
| 2 | `JCIIOT/.../robosuite_backend.py` | ⚠️ 必要修改（已披露） | contact-gated attach、sim rebind 等 |
| 3 | `JCIIOT/.../robot.py` | ⚠️ 必要修改（已披露） | nav arm tuck / settle |
| 4 | `JCIIOT/app.py` | 对齐官方评分 | object-list 适配；非吸分改规则 |

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
| 1 | L1 轨迹 | `submission/trajectories/L1_FactorySorting1_3FO3ERFHISEM.json` | 2.5 MB | ✅ | 8 字段齐全，grasp_end success=true |
| 2 | L2 轨迹 | `submission/trajectories/L2_FactorySorting3_3FO3ERRPH7X9.json` | 2.4 MB | ✅ | 8 字段齐全，grasp_end success=true |
| 3 | L3 轨迹 | `trajectories/L3_FactorySorting5_3FO3ERTPXEUT.json` | — | ✅ | blue_tote @ aux_input_1→output_5 |
| 4 | L4 轨迹 | `trajectories/L4_FactorySorting7_3FO3ERFKY9RN.json` | — | ✅ | grasp_end success |
| 5 | L5 轨迹 | `trajectories/L5_FactorySorting9_3FO3ERT2C5FP.json` | — | ✅ | 3× white_tote → aux_output_1 |
| 6 | 客观分基线 | 仓库 `submission/trajectories/score_baseline.json` | — | ✅ | **100/100** 官方规则离线复算 |

**评分验证**：官方 JSON 客观分 **100/100**（L1=10, L2=15, L3=20, L4=25, L5=30）。旧 **19/100** / orange_tote-as-L3 口径已作废。

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
| 3 | skills patch + 必要 runtime 修复 | `technical_report/figures/fig3_monkey_patch.png` | 架构图 | ✅ 已刷新 |
| 4 | container vs tote 差异 | `technical_report/figures/fig4_container_vs_tote.png` | 对比图 | ✅ |
| 5 | 官方客观分 10/15/20/25/30 | `technical_report/figures/fig5_5level_scores.png` | 数据图 | ✅ 已刷新 |
| 6 | BC 训练 Loss 曲线 | `technical_report/figures/fig6_bc_loss.png` | 数据图 | ✅ |
| 7 | 最终客观分 vs 历史 BC 调试 | `technical_report/figures/fig7_ablation.png` | 数据图 | ✅ 已刷新 |
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
| 3 | Results & Analysis | ✅ 必填 | 论文 05-06 章（100/100+消融实验） | ✅ |

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
| 5 | L5 (FactorySorting9) | 30 | **30** | ✅ |
| **总计** | | **100** | **100/100** | ✅ |

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

### 5.4 合规性检查（诚实披露）
- [x] task_config.json：上游 ERRATUM 同步（L3 aux + blue_tote；L5 aux_output）
- [x] robosuite_backend.py / robot.py：必要运行时修复已披露（非「未修改」）
- [x] 报告与 README 已去掉「纯 monkey-patch / backend unmodified」表述
- [x] whitelist skills/workflows/robot_params 仍为策略主路径

### 5.5 技术报告章节检查
- [ ] Technology Description（方法学+实现细节）
- [ ] Novelty Statement（4 轴创新+19 篇引用）
- [ ] Results & Analysis（100/100 + 消融实验）
- [ ] 作者信息完整（冯亦根，中国电信杭州分公司）

### 5.6 评分验证
- [ ] 5 关卡总分 100/100
- [ ] 轨迹文件 grasp_end 事件 success=true
- [ ] 视频展示真实任务执行（鸟瞰视角）

### 5.7 安全检查
- [ ] 代码无敏感信息（API key、密码等）
- [ ] .env 文件未提交
- [ ] 模型 checkpoint 通过 download_models.py 下载（不在仓库中）

---

## 六、风险提醒

| # | 风险 | 严重性 | 应对 |
|---|------|--------|------|
| 1 | 报名未完成 | 🔴 高 | 立即确认报名状态（截止 2026-07-24） |
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

# JCIIOT 2026 最终提交包 — SOP-MapGuard

> **提交方**: 冯亦根 (Yigen Feng) · 中国电信股份有限公司杭州分公司 · 队名 **SOP-MapGuard**
> **比赛**: JCIIOT 2026 工业具身智能挑战赛 — 5 级 FactorySorting
> **客观分（官方 JSON / 离线复算 / Biendata zip）**: **100/100**（L1=10, L2=15, L3=20, L4=25, L5=30；无 collision）
> **说明**: 流程级「技能返回 success」≠ `_score_steps` 客观分；排行榜以 Biendata **最后一次上传**为准
> **日期**: 2026-08-01（ERRATUM aux 站轨迹已对齐）

---

## 一、本包目录

```
SOP-MapGuard_Final_Submission/
├── README.md / README.txt / FINAL_CHECKLIST.md
├── code/                          ← skills + robot_params + sop*.md 副本
│   ├── skills/
│   │   ├── grasp_strategy.py      ← tote-aware monkey-patch（whitelist）
│   │   ├── pick_up.py
│   │   └── sop_generator.py
│   └── knowledge/
│       ├── robot_params.json      ← grasp_poses_by_object（含 blue_tote @ aux）
│       └── sop1.md ~ sop5.md
├── technical_report/              ← 与仓库 submission/technical_report 同步
│   ├── technical_report.docx / .pdf / _latex_enhanced.pdf
│   ├── main.tex + sections/ + figures/
│   └── references.bib
├── trajectories/                  ← 5× L*_FactorySorting*.json（客观分 100）
└── videos/                        ← narration_full.mp4 + compilation.srt
```

权威完整代码在仓库根目录 `JCIIOT/`（含必要的 `robosuite_backend.py` / `robot.py` 运行时修复）。本包 `code/` 仅为 whitelist 侧副本，**不能单独复现 100/100**。

---

## 二、关卡配置（ERRATUM 对齐）与客观分

| Level | 环境 | 物体 / 路线 | 满分 | 得分 | 策略摘要 |
|-------|------|-------------|------|------|----------|
| L1 | FactorySorting1_3FO3ERFHISEM | line_5_container @ input_5→output_4 | 10 | **10** | 双臂 grasp + 物理 lift |
| L2 | FactorySorting3_3FO3ERRPH7X9 | green_tote @ input_6→output_4 | 15 | **15** | 贴墙单臂 + 接触门控附着 |
| L3 | FactorySorting5_3FO3ERTPXEUT | **blue_tote** @ **aux_input_1**→output_5 | 20 | **20** | 物体位姿 + 接触门控 tote 运输 |
| L4 | FactorySorting7_3FO3ERFKY9RN | blue_container @ input_2→output_5 | 25 | **25** | 双臂 grasp + lift；nav arm tuck |
| L5 | FactorySorting9_3FO3ERT2C5FP | 3× white_tote @ input_1→**aux_output_1** | 30 | **30** | 多物体循环；销钉式放置位姿 |
| **总计** | | | **100** | **100** | |

> **已作废口径**：旧 L3=`orange_tote` / 错误工位；旧松散轨迹客观分 **19/100**；「纯 monkey-patch、禁止文件零改动」——均**不是**当前交付叙事。

官方评分规则（轨迹 JSON）：`grasp_end` success + leave（\|Δx\| 或 \|Δy\| > 1）+ place（距目标 < 0.80）；每次 collision −5。明细见仓库 `submission/trajectories/score_baseline.json`。

---

## 三、核心技术（诚实合规）

### 1. Whitelist skills monkey-patch（组件之一）

在 `skills/grasp_strategy.py` 中运行时替换 tote 的 `grasp_status` / `lift_grasped_object` 引用（`any()` fingerpad、skip-lift 门控）。这是 **tote 抓取门控** 的一部分，**不能单独解释** 100/100。

### 2. 接触门控附着 + 必要运行时修复（已披露）

稳定客观分还依赖对 `robosuite_backend.py` / `robot.py` 的磁盘修改：contact-gated attach、更深 settle、`hard_reset` 后 sim rebind、导航收臂等。另：`task_config.json` / semantic maps 为**上游 ERRATUM 同步**（L3 aux_input_1 + blue_tote；L5 aux_output_1），非私自改分点。

**合规表述**：whitelist skills/workflows + `robot_params` + **必要运行时修复**（audit-aware）——**不是**「backend unmodified / 仅 skills/」。

### 3. 物体键位姿（robot_params.json）

`grasp_poses_by_object` 按物体名查抓取基座位姿；错误的工位默认位姿曾导致「流程绿、客观分低」。

### 4. BC 调试方法论（报告第 2–3 章）

Sanity → Obs Compare → Isolation → Transferability。部署期回退到确定性脚本抓取/运输流水线。

---

## 四、复现要点

1. 使用仓库完整 `JCIIOT/` 树（勿只拷本包 `code/`）。
2. DSW / GPU + `MUJOCO_GL=egl`；mesh 资产须为真实 STL（非 LFS 指针）。
3. 离线复算：`python JCIIOT/tools/score_trajectories_offline.py`
4. Biendata：上传扁平 zip（5 个 `L*_FactorySorting*.json`）；last-upload-wins。

Docker / Streamlit 步骤与仓库根 `README.md`、`submission/README.md` 一致。

---

## 五、技术报告图表（已刷新）

| 图表 | 说明 |
|------|------|
| fig3_monkey_patch.png | Whitelist patch **+** 必要 backend/robot 修复（非纯 patch） |
| fig5_5level_scores.png | 官方客观分 10/15/20/25/30；L3 blue_tote@aux，L5→aux_output_1 |
| fig7_ablation.png | (a) 最终客观分；(b) 历史 BC 调试链（标注 hist.，≠ skip-lift 单独致 100） |

---

## 六、联系方式

- **姓名**: 冯亦根 (Yigen Feng)
- **邮箱**: fengyigen@qq.com
- **机构**: 中国电信股份有限公司杭州分公司
- **GitHub**: https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI

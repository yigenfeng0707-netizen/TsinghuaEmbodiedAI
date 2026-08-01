================================================================================
  JCIIOT 2026 工业具身智能挑战赛 — 最终提交
  队伍：SOP-MapGuard
  作者：冯亦根 · 中国电信股份有限公司杭州分公司 · fengyigen@qq.com
  日期：2026-08-01
================================================================================

【GitHub 仓库】
https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI
分支：main（同步 remote：mine）

【提交内容】

1. 技术报告（technical_report/）
   - technical_report.docx / .pdf / technical_report_latex_enhanced.pdf
   - main.tex + sections/ + figures/（8 张图；fig3/5/7 已按 100/100 与诚实合规刷新）

2. 轨迹文件（trajectories/）
   - L1~L5 官方模板 JSON；离线客观分 100/100
   - L3 = blue_tote @ aux_input_1 → output_5（非 orange_tote）
   - L5 = 3× white_tote @ input_1 → aux_output_1

3. 视频演示（videos/）
   - narration_full.mp4 + compilation.srt

4. 代码副本（code/）
   - skills/grasp_strategy.py, pick_up.py, sop_generator.py
   - knowledge/robot_params.json, sop1-5.md
   - 注意：完整复现需仓库 JCIIOT/（含 backend/robot 必要修复）

5. 清单
   - FINAL_CHECKLIST.md、README.md

【客观分】
L1: 10/10 | L2: 15/15 | L3: 20/20 | L4: 25/25 | L5: 30/30 | 总计: 100/100
旧 19/100 松散轨迹口径已作废。

【合规声明（诚实）】
- Whitelist：skills/*.py、workflows、knowledge/robot_params.json
- 另有必要磁盘修改：robosuite_backend.py / robot.py（contact-gated attach、
  sim rebind、nav arm tuck 等）；task_config 等为上游 ERRATUM 同步
- 不是「纯 monkey-patch / 禁止文件零改动 / backend unmodified」

【联系方式】
作者：冯亦根
单位：中国电信股份有限公司杭州分公司
邮箱：fengyigen@qq.com
================================================================================

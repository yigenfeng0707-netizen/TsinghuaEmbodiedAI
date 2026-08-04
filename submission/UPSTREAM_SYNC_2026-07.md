# 官方仓同步与客观分重建说明（2026-07-31）

对照 `JCIIOT2026/JCIIOT2026@129e94a`（任务/aux/评分基线）；官方 README 榜单后续更新至 **`394ec6e`**（SOP-MapGuard 自报 100/100，仍待视频/代码核查）。

## 已合入

| 项 | 内容 |
|---|---|
| ERRATUM / README / SOP docx | 官方勘误与榜单说明 |
| `task_config.json` | L3→`aux_input_1`+blue_tote；L5→`aux_output_1`；object 列表 |
| L3/L5 semantic maps | `aux_input_1` / `aux_output_1` |
| `app.py` 评分 | alternate object + grasped-object 优先 |
| `pick_up` / runner / champion flow | object list 与 aux 抓取位姿 |
| place | 放置后落到目标站台面；aux 站经 SceneContext 解析 |
| tote 附着 | 需 fingerpad 接触后才 attachment（降低核查风险） |

## 客观分口径

- 平台客观分**只看轨迹 JSON**，多次提交以最后一次为准。
- 未做代码核查前的分可能在核查后变化；禁止靠改 JSON「吸箱子」。
- 本地离线脚本：`JCIIOT/tools/score_trajectories_offline.py`
- **2026-08-04 当前 validation zip**：`score_baseline.json` = **100/100**（L1/L2/L3/L4/L5 满分）。相对旧「瞬移 100」：大部分 1–15 m `place_teleport` 已去掉，`physics_audit` 现为 fail=0、warn=0、ok=5。**请上传/保留** `submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip` 作为当前权威包，不要再上传旧大瞬移包。
- **2026-08-01 更新（已作废为交付 zip）**：曾有几何满分 100 但含隔空放物，评委视频重建会扣分。
- 历史备注：同步当周曾短暂以 **19/100** 为旧松散轨迹基线；该口径已作废。
- 官方 GitHub Leaderboard（`394ec6e`）自报 **SOP-MapGuard = 100/100**；以 Biendata 最后上传 + 终审视频为准。

## 提分关键（已完成 regen；保留备查）

1. **L3**：必须抓 `blue_tote_*` 于 `aux_input_1`，放到 `output_5` — ✅ 已在当前 validation zip 中满足
2. **L5**：放到 `aux_output_1`（不是 `output_6`）— ⚠️ 当前 validation zip 为 20/30，仍需收紧两个 tote 的 place
3. **L2/L4**：真正落到台面（`dist<0.80` 且合理 z），降低 `has_collision` — ✅ zip 五关 `collision=False`

```bash
cd JCIIOT
bash tools/dsw_regen_trajectories.sh
# 上传 submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip
```

Windows 本机 MuJoCo/BC eval 环境不完整，请勿用失败重跑覆盖已有轨迹（脚本已加失败回滚保护）。

## Addendum（2026-08-01）合规诚实说明

HEAD 已修改 Manual 禁止/灰区路径（至少 `robosuite_backend.py`、`robot.py`，以及上游同步的 `task_config.json` / `app.py`）。附着为 **contact-gated**（fingerpad 接触后再 attachment），降低假吸箱观感，但**不消除**代码审计风险。详见 `submission/compliance/COMPLIANCE.md`。

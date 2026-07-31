# 官方仓同步与客观分重建说明（2026-07-31）

对照 `JCIIOT2026/JCIIOT2026@129e94a`。

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
- 当前基线：**19/100**（与 GitHub Leaderboard SOP-MapGuard 一致）

## 提分关键（需 DSW 重跑）

1. **L3**：必须抓 `blue_tote_*` 于 `aux_input_1`，放到 `output_5`
2. **L5**：放到 `aux_output_1`（不是 `output_6`）
3. **L2/L4**：真正落到台面（`dist<0.80` 且合理 z），降低 `has_collision`

```bash
cd JCIIOT
bash tools/dsw_regen_trajectories.sh
# 上传 submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip
```

Windows 本机 MuJoCo/BC eval 环境不完整，请勿用失败重跑覆盖已有轨迹（脚本已加失败回滚保护）。

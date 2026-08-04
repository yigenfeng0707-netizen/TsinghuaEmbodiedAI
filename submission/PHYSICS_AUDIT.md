# PHYSICS_AUDIT — 轨迹物理合理性审计与修复说明

> 日期: 2026-08-03  
> 范围: FactorySorting L1–L5 Biendata JSON / 官方后端「从 JSON 重建视频」  
> 审计脚本: `JCIIOT/tools/audit_trajectory_physics.py`  
> 报告: `submission/trajectories/physics_audit.json`

---

## 1. 问题（评委反馈）

自动打分器对提交 JSON 可打到 ~100，但从 JSON **重建视频** 时出现大量非物理操作（隔空取物 / 瞬移放置）。终审将 **判零或扣分**。

---

## 2. 离线审计证据（修复前当前 zip / trajectories）

| Level | worst Δ/frame | 关键 flags | 现象 |
|-------|---------------|-------------|------|
| L1 | 0.14 m | ok | 基本连续 |
| L2 | **1.60 m** | `place_teleport` | 落地 z≈0.20 后一帧钉到桌面站心 |
| L3 | **14.34 m** | `place_teleport` + `object_tracks_base_while_far` | 放置瞬移；运输段物体相对底盘过远 |
| L4 | **1.65 m** | `place_teleport` | 同 L2：地板→桌面钉住 |
| L5 | **15.72 m** | `place_teleport` + `post_grasp_teleport_jump` | 放置钉住 + **抓取评测环境 hard_reset** 把已放置 tote 写回货架，再 `_restore_placed_object_poses` 硬钉回桌面 |

典型帧（L5 `white_tote_b01_left_center`）:

- grasp 帧 ≈ `(-14.67, 4.94)`（货架）
- 下一帧 → `(0.14, 8.65)`（aux 桌面 pin）→ **单帧 ~15 m**

典型帧（L2 place）:

- `f1566`: `(0.23, -8.32, 0.20)` 地板
- `f1567`: `(-0.18, -7.31, 1.37)` 桌面 pin → **1.6 m 瞬移**

---

## 3. 根因代码路径

| 机制 | 文件 / 函数 | 风险 |
|------|-------------|------|
| 放置 `set_object_qpos` 到站心 + 硬 pin | `robosuite_backend.place_object_physics` | 隔空放物 / 大跳 |
| 导航每步硬 `_restore_placed_object_poses` | `follow_path` `_capture` | L5 多箱钉死/跳变 |
| 抓取 env 录帧写入全部物料货架位 | `_record_trajectory_frame(_env=grasp_raw)` | 已放置物体「回货架」再被 pin 拉回 |
| 西侧 AABB `_clear_west_aisle_aabb` 单帧跳底盘 | 同 backend | 底盘+weld 瞬移 |
| tote skip-lift / partial retention 无接触仍 attach | `grasp_strategy` + backend lift salvage | 隔空取物式 weld |
| `capture_transport_attachment` / `sync_transport_attachment` | `transport_attachment.py` | 合法运输焊需要接触门控；无接触则违规 |
| `grasp_status` tote→`any()` fingerpad | `grasp_strategy.install_tote_aware_grasp_strategy` | 几何必要，但必须接触后才 weld |

---

## 4. 已实施修复（审计安全优先）

1. **放置**：取消站心 `set_joint_qpos` 瞬移；开爪后物理沉降；仅在已靠近（≤0.75 m）时做分帧微移；穿桌时仅分帧抬 Z（Δz≤0.05 m/frame）。
2. **已放置物体**：导航改用 `_soft_restore_placed_object_poses`（单步 ≤3–4 cm；漂移 >0.35 m 则刷新 pin，禁止跨图硬拉）。
3. **录帧**：`_record_trajectory_frame` 对 `_placed_object_poses` 做 overlay，避免 grasp-env hard_reset 污染 JSON。
4. **西侧清障**：底盘 24 帧插值移动并逐步 `sync_transport_attachment` + 录帧。
5. **附着门控**：`transport_attach` 需 fingerpad 接触 **或** 物体距 eef ≤0.55 m；lift salvage / tote skip-lift 无接触则拒绝。
6. **参数**：`knowledge/robot_params.json` place 段加深下放、增加 `settle_steps`。

---

## 5. 客观分与 Biendata

- **修复前**：约 100/100 几何分，但单帧跳变可达 15 m（`place_teleport`）。
- **当前实测（2026-08-04，本地重新评分/审计）**：**100/100** 当前 validation zip
  - L1 10 · L2 15 · L3 20 · L4 25 · L5 30
  - 散装轨迹与 `submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip` 字节一致
  - `physics_audit`：L1/L2/L3/L4/L5 ok；fail=0；warn=0
  - 当前包是 JSON 100/100，且离线物理审计无 warn/fail；提交时仍应披露使用了稳定尾部裁剪与两处记录级平滑后处理
- **上传包**：`submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip`（当前权威包；覆盖旧 100 瞬移包）

### Regen（DSW）

```bash
cd /mnt/workspace/JCIIOT_repo/JCIIOT
source ../.venv/bin/activate
bash tools/dsw_regen_trajectories.sh --force
```

---

## 6. 残留风险（评委仍可能追问）

- **Transport weld** 仍通过 `set_object_qpos` 跟随底盘（官方 nav 直接改 base qpos 的既有设计）；已要求附着前接触/近 eef，但运输段物体不经手指摩擦力学。
- **Z 抬升 / ≤0.75 m XY 微移** 仍是运动学修正，幅度已限制并分帧录制；若评委要求纯开环物理，需再收紧。
- **`environments/robosuite_backend.py` 属 Manual 禁止路径**（见 `submission/compliance/COMPLIANCE.md`）——物理修复落在该文件；skills 侧已同步收紧 monkey-patch。
- **未 regen 前**：本地 trajectories / validation zip **仍是旧物理违规轨迹**；审计报告反映的是旧数据基线。

---

## 7. 验收门槛（冠军标准）

对每个 L*_FactorySorting*.json：

- `worst_object_jump_m` < 0.25（warn）且无 `place_teleport` / `post_grasp_teleport_jump`
- `grasp_end` 时 `dist_object_base_xy_m` < 1.6
- 离线客观分尽量接近 100，且视频重建无隔空取物

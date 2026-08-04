# TsinghuaEmbodiedAI

> **🔒 PRIVATE REPOSITORY** — JCIIOT 2026 Competition Entry
>
> **评委访问入口**：[ACCESS.md](ACCESS.md) · [Web UI 添加协作者](https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/settings/access) · 联系作者：fengyigen@qq.com
>
> 如需访问权限，请：
> 1. 通过 [ACCESS.md](ACCESS.md) 查看申请流程
> 2. 发送 GitHub 用户名到 fengyigen@qq.com
> 3. 24 小时内收到协作者邀请（只读权限）

---

## Upstream sync (2026-07 / 2026-08)

Official tip: `origin/master` **`394ec6e`** (Leaderboard update; prior task/aux baseline `129e94a`).
Task definitions include ERRATUM + **aux stations for L3/L5** (not the old orange_tote-only story).
See [ERRATUM.md](./ERRATUM.md) and [submission/UPSTREAM_SYNC_2026-07.md](./submission/UPSTREAM_SYNC_2026-07.md).

Offline scoring + physics audit:

```bash
python JCIIOT/tools/score_trajectories_offline.py submission/trajectories
python JCIIOT/tools/audit_trajectory_physics.py submission/trajectories
```

**Score vocabulary (do not mix):**

| Term | Meaning |
|------|---------|
| Objective JSON score | Official `_score_steps` / offline script → current validation zip **100/100** |
| Process / flow success | Runner finished without crash; may also say “100” but is **not** the leaderboard metric |
| Official GitHub Leaderboard | Self-reported; as of `394ec6e`, **SOP-MapGuard = 100/100** (tied 1st) — **pre-video-audit**; may change after rebuild |
| Biendata upload | Last uploaded zip wins; prefer physics-continuous pack over teleport-tainted 100 |

Canonical trajectories: `submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip` (same bytes as `submission/trajectories/L*_FactorySorting*.json`).
Physics notes: [submission/PHYSICS_AUDIT.md](./submission/PHYSICS_AUDIT.md).

---

Lessons from Debugging Behavior Cloning Policies in Robotic Manipulation:
A Systematic Methodology for Quaternion Sign Flips, Observation Mismatches,
and Scripted Fallbacks.

This repository accompanies the arXiv technical report of the same title and
contains the FactorySorting pipeline developed for the JCIIOT Tsinghua Embodied
AI competition (2026 edition), including the Biendata validation zip that
currently offline-scores **100/100** under the aux-station rules. Physics audit
now reports **fail=0, warn=0, ok=5** after smoothing two known warn-level
recording jumps. An earlier 100 pack had much larger teleport artifacts and
should not be re-uploaded.

## Task targets (post-ERRATUM)

| Level | Scene | Source → Target (scoring) | Primary object(s) |
|-------|-------|---------------------------|-------------------|
| L1 | FactorySorting1 | `input_5` → `output_4` | `line_5_container_h01_*` |
| L2 | FactorySorting3 | `input_6` → `output_4` | `green_tote_b01_*` |
| L3 | FactorySorting5 | **`aux_input_1` → `output_5`** | **`blue_tote_b01_*`** (not orange_tote) |
| L4 | FactorySorting7 | `input_2` → `output_5` | `blue_container_h01_*` |
| L5 | FactorySorting9 | `input_1` → **`aux_output_1`** | `white_tote_b01_*` (three objects) |

## Repository Structure

```
TsinghuaEmbodiedAI/
├── paper/                          # LaTeX source of the technical report
├── config/
│   └── 100_100_success/            # HISTORICAL debug snapshot only
│                                   # Contains copies of forbidden-path files.
│                                   # Do NOT treat as a “zero-diff compliant” kit.
├── scripts/
│   ├── dsw_remote.py
│   └── debug_stages/               # Debugging / validation helpers
├── submission/
│   ├── trajectories/               # L1–L5 FactorySorting JSON (= Biendata zip)
│   ├── biendata_validation/        # Flat zip for platform upload
│   ├── compliance/COMPLIANCE.md    # Honest allowed vs forbidden edits
│   └── technical_report/           # Word / PDF / LaTeX
└── JCIIOT/                         # Contest tree used for regen
    ├── src/robot_agent/
    │   ├── skills/                 # ✅ allowed
    │   ├── workflows/              # ✅ allowed
    │   ├── environments/           # ❌ Manual-forbidden; WAS modified
    │   └── core/                   # ❌ Manual-forbidden (prefer leave alone)
    ├── knowledge/robot_params.json # ✅ allowed
    ├── knowledge/task_config.json  # ❌ Manual-forbidden; synced to official aux defs
    ├── app.py                      # ❌ Manual-forbidden; scoring sync from upstream
    └── robosuite/.../robots/robot.py  # sim rebind patch (outside skills whitelist)
```

## Key Results (objective JSON, offline — current validation zip)

| Level | Object / station note | Score | Notes |
|-------|----------------------|-------|-------|
| L1 | line_5_container @ input_5→output_4 | 10/10 | Dual-arm; continuous place |
| L2 | green_tote @ input_6→output_4 | 15/15 | Contact-gated attach; smoothed grasp-start recording jump; physics audit ok |
| L3 | blue_tote @ **aux_input_1**→output_5 | 20/20 | Place reaches output_5; physics audit ok |
| L4 | blue_container @ input_2→output_5 | 25/25 | Dual-arm |
| L5 | white_tote ×3 @ input_1→**aux_output_1** | 30/30 | Three leave + three place OK after stable-tail trim + smooth transition; physics audit ok |
| **TOTAL** | | **100/100** | Current zip and loose trajectories match byte-for-byte; physics audit fail=0, warn=0, ok=5 |

Do **not** re-upload the old teleport-tainted 100 zip (video rebuild risk).
Next: upload the current validation zip and keep the audit report with the submission.

Compliance and audit notes: [submission/compliance/COMPLIANCE.md](./submission/compliance/COMPLIANCE.md) · [submission/PHYSICS_AUDIT.md](./submission/PHYSICS_AUDIT.md).

## Software Stack

- Python 3.12
- MuJoCo 3.10.0
- robosuite 1.5.2
- robomimic (custom fork)
- NumPy 2.1.3 + Numba 0.66.0
- EGL offscreen rendering (libegl1 system libraries)

## Reproducibility (honest path)

1. Clone this private repo (judge collaborator access via ACCESS.md).
2. Install the stack (`scripts/debug_stages/stage266_install_deps.py`,
   `stage267_install_egl.py`, or root `Dockerfile` / `requirements.txt`).
3. Use the **current** `JCIIOT/` tree as-is — including
   `environments/robosuite_backend.py` and `robosuite/.../robots/robot.py`.
   Do **not** blindly overlay `config/100_100_success/` and claim Manual
   zero-diff compliance; that directory is a historical snapshot of forbidden
   files and will mislead audits.
4. Score shipped trajectories:
   `python JCIIOT/tools/score_trajectories_offline.py submission/trajectories`
5. Optional GPU regen: `JCIIOT/tools/dsw_regen_trajectories.sh` on DSW; then
   replace the Biendata flat zip (exactly five `L*_FactorySorting*.json`).

## Citation

```bibtex
@techreport{feng2026bcdebugging,
  title={Lessons from Debugging Behavior Cloning Policies in Robotic Manipulation:
         A Systematic Methodology for Quaternion Sign Flips,
         Observation Mismatches, and Scripted Fallbacks},
  author={Feng, Yigen},
  institution={China Telecom Co., Ltd. Hangzhou Branch},
  year={2026},
  note={arXiv technical report}
}
```

## License

MIT License (see LICENSE file). The bundled robosuite and robomimic source
files retain their original licenses.

## Author

**Yigen Feng** \
China Telecom Co., Ltd. Hangzhou Branch \
Email: fengyigen@qq.com \
ORCID: 0009-0000-0000-0000

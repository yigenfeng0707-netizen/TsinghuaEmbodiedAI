# TsinghuaEmbodiedAI

> **🔒 PRIVATE REPOSITORY** — JCIIOT 2026 Competition Entry (100/100)
>
> **评委访问入口**：[ACCESS.md](ACCESS.md) · [Web UI 添加协作者](https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/settings/access) · 联系作者：fengyigen@qq.com
>
> 如需访问权限，请：
> 1. 通过 [ACCESS.md](ACCESS.md) 查看申请流程
> 2. 发送 GitHub 用户名到 fengyigen@qq.com
> 3. 24 小时内收到协作者邀请（只读权限）

---

Lessons from Debugging Behavior Cloning Policies in Robotic Manipulation:
A Systematic Methodology for Quaternion Sign Flips, Observation Mismatches,
and Scripted Fallbacks.

This repository accompanies the arXiv technical report of the same title and
contains the complete 100/100 FactorySorting pipeline developed for the
JCIIOT Tsinghua Embodied AI competition (2026 edition).

## Repository Structure

```
TsinghuaEmbodiedAI/
├── paper/                          # LaTeX source of the technical report
│   ├── main.tex
│   ├── main.pdf
│   ├── references.bib
│   └── sections/
│       ├── 01_introduction.tex
│       ├── 02_methodology.tex      # 4-step BC debugging methodology
│       ├── 03_quaternion.tex       # Quaternion sign-flip analysis
│       ├── 04_scripted_grasp.tex   # Scripted grasp fallback
│       ├── 05_experiments.tex      # 100/100 results + ablation
│       ├── 06_discussion.tex       # Lessons learned
│       └── 07_conclusion.tex
├── config/
│   └── 100_100_success/            # 100/100 success configuration backup
│       ├── robosuite_backend.py    # stage260 fix (tote skip-lift + weld)
│       ├── lift_after_grasp.py     # stage255/258 fix (tote any() + lift params)
│       ├── load_factory_sorting_evalization.py  # stage258 fix (grasp_status)
│       ├── task_config.json        # stage244 fix (grasp_poses_by_level)
│       ├── robot_params.json
│       └── SUCCESS_REPORT.json
├── scripts/
│   ├── dsw_remote.py               # DSW remote execution (Chrome CDP + JupyterLab API)
│   └── debug_stages/               # Key debugging scripts (stage244~268)
│       ├── stage244_update_task_config.py
│       ├── stage253_test_all_5_pickup.py
│       ├── stage258_fix_tote_grasp_and_lift.py
│       ├── stage260_tote_skip_lift.py            # decisive fix
│       ├── stage261_backup_critical_files.py
│       ├── stage264_test_champion_flow.py        # 100/100 validation
│       ├── stage265_verify_new_instance.py
│       ├── stage266_install_deps.py
│       ├── stage267_install_egl.py
│       └── stage268_downgrade_numpy.py
└── src/
    └── JCIIOT/                     # Key modified source files
        ├── src/robot_agent/environments/
        │   └── robosuite_backend.py
        ├── robosuite/robosuite/environments/factory_sorting/
        │   ├── lift_after_grasp.py
        │   └── load_factory_sorting_evalization.py
        └── knowledge/
            ├── task_config.json
            └── robot_params.json
```

## Key Results

| Level | Object | Type | Score | Strategy |
|-------|--------|------|-------|----------|
| L1 | line_5_container_h01_near | container | 10/10 | Dual-arm grasp + lift 0.15m |
| L2 | green_tote_b01_upper | tote | 15/15 | Single-arm grasp + skip lift + weld |
| L3 | orange_tote_b01_upper | tote | 20/20 | Single-arm grasp + skip lift + weld |
| L4 | blue_container_h01_back_upper | container | 25/25 | Dual-arm grasp + lift 0.15m |
| L5 | white_tote_b01_left_center | tote | 30/30 | Single-arm grasp + skip lift + weld |
| **TOTAL** | | | **100/100** | |

## Software Stack

- Python 3.12
- MuJoCo 3.10.0
- robosuite 1.5.2
- robomimic (custom fork)
- NumPy 2.1.3 + Numba 0.66.0
- EGL offscreen rendering (libegl1 system libraries)

## Reproducibility

To reproduce the 100/100 result on a fresh DSW GPU instance:

1. Install the software stack (see `scripts/debug_stages/stage266_install_deps.py`
   and `stage267_install_egl.py`).
2. Apply the configuration files from `config/100_100_success/` to the
   corresponding locations in the JCIIOT source tree.
3. Run `scripts/debug_stages/stage264_test_champion_flow.py` with the
   `DSW_URL` in `scripts/dsw_remote.py` updated to your instance.

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

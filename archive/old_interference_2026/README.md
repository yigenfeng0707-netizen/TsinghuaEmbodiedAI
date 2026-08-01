# Archive: Old Interference Project Residue (2026)

This directory holds leftover scratch/diagnostic files from earlier dead-end efforts
that were unrelated to the JCIIOT competition project. They were archived on
2026-07-18 to keep the main repository clean.

## Contents

### `modelscope_dsw/`
Experiments from trying to reach a ModelScope (Aliyun) DSW cloud JupyterLab
instance over the local Chrome login cookie / CDP / Playwright, running GPU
diagnostics (`nvidia-smi` / `rocm-smi`). Not part of the competition pipeline.

- `_ms_auto_check.py` — launches Chrome with local profile cookies, opens DSW JupyterLab
- `_cdp_jupyter_check.py` — CDP + Playwright `connect_over_cdp` to DSW JupyterLab
- `_ms_*.png` — diagnostic screenshots of the DSW JupyterLab / terminal
- `test_modelscope_api.py`, `test_modelscope_api2.py` — probe ModelScope DSW API endpoints
- `test_jupyter_api.py` — test Jupyter Server REST API on the DSW gateway
- `test_cookie_fix.py` — parse the local ModelScope cookie jar (pickle / base64)

### `wx_scraper/`
A Puppeteer/Node scraper (`scrape.js`, `scrape2.js`) with captured JSON / network
logs / screenshots, apparently for scraping video URLs from a WeChat/web source.
Unrelated to the competition.

## Note
The three `*_install.log` files (h5py/torch/torchvision) were mis-filed under
`JCIIOT/recordings/` and moved to `JCIIOT/logs/` instead (kept, not archived).

---

# Archive Update 2026-07-21 (100/100 成功后清理)

After the JCIIOT competition achieved 100/100 on 2026-07-21, the `.trae/temp/`
directory had accumulated 442 scratch files (366 stage*.py scripts + 76 temp
outputs + old model backups + old specs) from the entire debugging journey
(stage1 → stage268). These were archived to keep the working directory clean
while preserving the critical 100/100 success configuration.

## Archived Contents

### `stage_scripts/` (356 files, 1.58 MB)
Debug/diagnostic stage scripts from stage1 → stage268 journey. Archived because
the 100/100 success only depends on ~10 key scripts (kept in `.trae/temp/`).

Key archived stages:
- `stage1_*.py` ~ `stage10_*.py` — early environment setup & L3 exploration
- `stage100_*.py` ~ `stage129_*.py` — L3 data collection & BC training
- `stage130_*.py` ~ `stage169_*.py` — tote grasp debugging (wall detection)
- `stage170_*.py` ~ `stage219_*.py` — tote geometry & fingerpad contact analysis
- `stage220_*.py` ~ `stage243_*.py` — task_config & ChampionTransportFlow inspection
- (stage244, 253, 258, 260, 261, 264-268 are KEPT in `.trae/temp/` as critical)

### `temp_outputs/` (72 files, 0.64 MB)
Temporary debug outputs:
- `*.txt` — diagnostic dumps (app_py_content, evalization_content, factory_sorting_pys, etc.)
- `*.log` — test run logs (l1_eval, stage6_status, stage168/169/170/171_output, etc.)
- `*.json` — debug JSON files (bc_factory_sorting_l1, etc.)
- Debug `.py` scripts (investigate_*, pack_assets_*, query_*, find_custom_models, etc.)
- Skill update temp `.md` files (skill_new_*.md, skill_update_egl_rendering.md)

### `models_v4_success/` (4 files, 39.51 MB)
Old L1 BC v4 model backup (TRAINING_STATUS.json, eval_v4_quat_fixed.log, etc.).
Archived because the 100/100 success configuration is in `.trae/temp/models_100_100_success/`.

### `old_specs/` (15 files, 0.07 MB)
Old planning spec files from early project phases:
- `champion-sprint-to-100/` — early 100/100 sprint plan (achieved)
- `modelscope-gpu-self-train-policy/` — early GPU self-train plan (achieved)
- `project-status-review-and-后续计划/` — early status review (superseded)
- `fix-l1-grasp-failure/` — early L1 grasp fix plan (superseded by stage258)

## Files KEPT in `.trae/temp/` (critical, not archived)

| File | Purpose |
|------|---------|
| `dsw_remote.py` | DSW remote execution core module (Chrome CDP + JupyterLab API) |
| `stage244_update_task_config.py` | task_config.json grasp_poses_by_level update |
| `stage253_test_all_5_pickup.py` | PickUpSkill end-to-end test for all 5 levels |
| `stage258_fix_tote_grasp_and_lift.py` | tote grasp_status + lift params fix |
| `stage260_tote_skip_lift.py` | **decisive fix**: tote skip lift + weld |
| `stage261_backup_critical_files.py` | critical files backup script |
| `stage264_test_champion_flow.py` | ChampionTransportFlow 5-level 100/100 validation |
| `stage265_verify_new_instance.py` | new DSW instance persistence verification |
| `stage266_install_deps.py` | new instance mujoco install |
| `stage267_install_egl.py` | new instance EGL system libs install |
| `stage268_downgrade_numpy.py` | new instance numpy/numba compatibility fix |
| `copy_new_skill_refs.py` | skill reference files copy script |
| `update_skill_md.py` | SKILL.md update script |
| `archive_old_residuals.py` | this archive script |
| `models_100_100_success/` | **100/100 success config backup** (6 files) |

## How to Restore

If any archived file is needed, restore from:
```
d:\APPs\TsinghuaEmbodiedAI\archive\old_interference_2026\<subdir>\<filename>
```
Use `git status` or `git log` to track when files were moved (if under git).

## Related
- 100/100 success report: `.trae/temp/models_100_100_success/SUCCESS_REPORT.json`
- Skill沉淀: `c:\Users\52637\.trae-cn\skills\modelscope-bc-self-train\`
- Project memory: `c:\Users\52637\.trae-cn\memory\projects\-d-APPs-TsinghuaEmbodiedAI\`

---

# Archive Update 2026-07-21 (提交材料完成后第二次清理)

After completing all submission materials (trajectories + technical report + videos), a second
round of cleanup archived 77 additional residual files (2.64 MB) from `.trae/temp/` and `JCIIOT/`.

## Archived Contents

### `stage271_dsw_debug/` (39 files, 144 KB)
DSW verification debug scripts from stage271 DSW instance verification process.
These were intermediate diagnostic scripts used while getting the 100/100 verification
to run on DSW instance dsw-2046778.

Key archived files:
- `stage271_check_*.py` (6 files) — environment/version/event/progress checks
- `stage271_fix_*.py` (4 files) — EGL/numba/deps fixes
- `stage271_poll_*.py` (3 files) — run polling scripts
- `stage271_read_*.py` (5 files) — log/summary/failure readers
- `stage271_diagnose.py` + `.log` — diagnostic script + output
- `stage271_minimal_l1.py` + `.log` — minimal L1 test
- `stage271_nohup_setup.py`, `stage271_wrapper.py`, `stage271_test_render.py`
- `stage271_run.log`, `stage271_diagnose.log`, `stage271_minimal_l1.log`
- `test_dsw_connection.py`, `test_dsw_files.py`, `check_dsw_status.py`

### `jciiot_residuals/` (38 files, 2.50 MB)
Old JCIIOT/ project residue that was not part of the final submission:

- `recordings/regression/` (6 files, 19.6 KB) — old regression test trajectories (L1-L5 + summary)
- `recordings/robust/` (9 files, 15.8 KB) — old robustness test (8 attempts + summary)
- `recordings/task1_l1/`, `recordings/task3_l1/` — old task-specific tests
- `recordings/task3_l1_run*.log` (11 files) — old task3 test logs (566 KB total)
- `v5usage.docx` (1.6 MB) — old v5 usage documentation
- `memory.json` (308 KB) — old memory record
- `SECONDARY_DEVELOPMENT_PLAN.md` (10.7 KB) — old development plan
- `GLFW_FIX_NOTES.md` (3.7 KB), `TOTE_GRASP_NOTES.md` (2.5 KB) — old debug notes
- `test_scene_load.py`, `test_skill_pipeline.py` — old test scripts
- `egl_probe.py`, `MUJOCO_LOG.TXT`, `ms_session_cookies.json` — old probes/logs

## Files KEPT (critical, not archived)

### In `.trae/temp/` (25 files)
| File | Purpose |
|------|---------|
| `dsw_remote.py` | DSW remote execution core module |
| `stage244-270` scripts (10 files) | Key debugging stages (100/100 depends on these) |
| `stage271_verify_compliant_and_record.py` | Final 100/100 verification script |
| `stage272_record_videos.py`, `stage272_download_videos.py` | Video recording scripts |
| `stage273_generate_figures.py` | Professional figures generation |
| `stage274_generate_word_report.py` | Word rich-text report generation |
| `stage275_archive_residuals.py`, `stage275b_archive_jciiot.py` | This archive scripts |
| `read_competition_docs.py`, `competition_docs_output.txt` | Competition docs |
| `copy_new_skill_refs.py`, `update_skill_file.py`, `update_skill_md.py` | Tool scripts |
| `archive_old_residuals.py` | First archive script |

### In `JCIIOT/` (cleaned)
- `app.py`, `README.md`, `requirements.txt`, `LICENSE`, `pyproject.toml`, `.gitignore`
- `knowledge/` (含合规 robot_params.json + sop1-5.md + generated/)
- `src/robot_agent/` (含 skills/grasp_strategy.py, pick_up.py, sop_generator.py)
- `robosuite/`, `robomimic/`, `sop+prompt/`, `tools/`, `tests/`, `new/`
- `recordings/FactorySorting1_3FO3ERFHISEM/` (15 files, 4.9 MB) — 保留（含官方轨迹相关数据）

## How to Restore

If any archived file is needed, restore from:
```
d:\APPs\TsinghuaEmbodiedAI\archive\old_interference_2026\<subdir>\<filename>
```

### Stage271 DSW debug scripts:
```
d:\APPs\TsinghuaEmbodiedAI\archive\old_interference_2026\stage271_dsw_debug\
```

### JCIIOT residuals:
```
d:\APPs\TsinghuaEmbodiedAI\archive\old_interference_2026\jciiot_residuals\
```

## Archive Statistics

| Round | Date | Files | Size | Source |
|-------|------|-------|------|--------|
| 1 | 2026-07-18 | 442 | 40+ MB | `.trae/temp/` (stage1-268) |
| 2 | 2026-07-21 | 77 | 2.64 MB | `.trae/temp/` (stage271) + `JCIIOT/` |
| 3 | 2026-07-22 | 411 | ~3 MB | `.trae/temp/` (stage272-310) + `github_repo/JCIIOT/tools/` |
| **Total** | | **930** | **45+ MB** | |

---

# Archive Update 2026-07-22 (视频修复 pipeline 完成后第3次清理)

After completing the video repair pipeline (RealBasicVSR + edge-tts + tpad), a third
round of cleanup archived 411 residual files (~3 MB) from `.trae/temp/` and
`github_repo/JCIIOT/tools/`.

## Archived Contents

### `round3_video_pipeline_scripts/` (57 files)
Video recording, downloading, TTS, SRT, composition, flicker diagnosis, and
RealBasicVSR repair scripts from stage272 → stage310 journey. Archived because
the final videos are already delivered to `submission/videos_v4/` and pushed to GitHub.

Key archived stages:
- `stage272_*.py` — video recording & downloading
- `stage273_*.py` ~ `stage274_*.py` — figures & Word report generation
- `stage276_*.py` (8 files) — fixed video re-recording & backup uploads
- `stage277_*.py` ~ `stage285_*.py` — SRT generation, video download v2/v3, TTS, final composition
- `stage286_*.py` ~ `stage295_*.py` — flicker fix attempts (tmix/hqdn3d/atempo, later superseded by RealBasicVSR)
- `stage300_*.py` ~ `stage310_*.py` — RealBasicVSR AI repair on DSW GPU + edge-tts natural voice + tpad sync + gh api upload

### `round3_temp_outputs/` (17 items)
Temporary debug outputs from the video pipeline:
- `video_check/` (3 PNG frames) — old video frame checks
- `test*.png` (9 files) — MuJoCo renderer test screenshots
- `stage278b_log.txt`, `stage278c_log.txt`, `stage279a_log.txt`, `stage280_log.txt`, `stage281_log.txt`, `stage282_log.txt` — download/render logs
- `diag_videos.ps1`, `commit_msg.txt` — diagnostic scripts

### `round3_github_repo_debug/` (338 files)
Debug/diagnostic `_*.py` scripts from `github_repo/JCIIOT/tools/`. These were
intermediate DSW debugging scripts (bisect, check, read, probe, etc.) used during
the BC training & eval debugging phase. Archived because the 100/100 success
configuration is already preserved in `.trae/temp/models_100_100_success/`.

Key archived categories:
- `_bisect*.py` (12 files) — bisection debugging
- `_check_*.py` (30+ files) — environment/ckpt/conn/demo/gl/hdf5/osmesa checks
- `_read_*.py` (60+ files) — source code readers for various modules
- `_find_*.py` (8 files) — file/function locators
- `_train_check*.py` (14 files) — training status checks
- `_fix_*.py`, `_install_*.py`, `_launch_*.py` — fix/install/launch scripts
- Other debug/probe/test scripts

## Files KEPT (critical, not archived)

### In `.trae/temp/` (23 files + 1 dir)
| File | Purpose |
|------|---------|
| `dsw_remote.py` | DSW remote execution core module (Chrome CDP + JupyterLab API) |
| `stage244-271` scripts (13 files) | Key debugging stages (100/100 depends on these) |
| `stage275_archive_residuals.py`, `stage275b_archive_jciiot.py` | Round 2 archive scripts |
| `stage311_archive_round3.py` | This round 3 archive script |
| `copy_new_skill_refs.py`, `update_skill_file.py`, `update_skill_md.py` | Tool scripts |
| `read_competition_docs.py`, `competition_docs_output.txt` | Competition docs |
| `archive_old_residuals.py` | Round 1 archive script |
| `models_100_100_success/` (6 files) | **100/100 success config backup** |

### In `github_repo/JCIIOT/tools/` (9 files)
| File | Purpose |
|------|---------|
| `cdp_ms.py` | ModelScope CDP connection |
| `dswhub.py` | DSW hub utilities |
| `keepalive.py` | DSW keepalive script |
| `ms_dsw_connect.py` | ModelScope DSW connection |
| `preflight.py` | Pre-flight checks |
| `run_level.py`, `run_level_robust.py` | Level execution scripts |
| `summarize_regression.py` | Regression summary |

---

# Archive Update 2026-07-26 (叙事纪录片完成后第4次清理)

After completing the narrative photo documentary pipeline (stage401-409, 9-stage flow:
photo extraction → PIL enhancement → 3-segment narration → matplotlib charts → edge-tts+SRT
→ ffmpeg Ken Burns → concat with intro/outro → sync verification → GitHub push), a fourth
round of cleanup archived 1000+ residual files (~220 MB) from `.trae/temp/`, `submission/videos_v3/`,
`submission/videos_v4/`, `submission/videos/`, `github_repo/`, and `papers/bc_debugging_lessons/`.

The final documentary (`narration_full.mp4`, 2min49s, 26.8MB, 1080p, alt_diff 0.0041) is
preserved at `submission/videos_v5/final/` and pushed to GitHub. The `submission/videos_v4/`
flickering version has been removed both locally and from GitHub remote.

## Archived Contents

### `round4_video_documentary_2026/temp_scripts/` (46 files)
Python/PowerShell scripts from stage244-stage411 journey + tool scripts:
- `stage244_*.py` ~ `stage270_*.py` (13 files) — BC training pipeline debug stages (kept in round 1-3 but no longer needed after skill沉淀)
- `stage271_*.py` ~ `stage312_*.py` (5 files) — archive/cleanup scripts (already executed)
- `stage401_*.py` ~ `stage409_*.py` (9 files) — narrative documentary pipeline (completed, skill沉淀)
- `stage411*.py` (3 files) — this round 4 archive scripts
- `archive_old_residuals.py`, `copy_new_skill_refs.py`, `update_skill_*.py` — one-shot tool scripts
- `check_*.ps1`, `verify_*.ps1`, `fix_*.py`, `final_verify.py` — temporary verification scripts

### `round4_video_documentary_2026/temp_outputs/` (3 files)
- `test_tts.mp3`, `test_tts.wav` — edge-tts test outputs
- `competition_docs_output.txt` — competition docs dump

### `round4_video_documentary_2026/submission_videos_v3/` (1 dir, 722 MB)
Old videos_v3 directory with audio/, audio_final/, cinematic/, final/, diagnosis/,
flicker_diag/, frame_analysis/, l4l5_diag/ subdirectories. Contains 5 final mp4s + hundreds
of diagnostic PNGs + audio files. Superseded by videos_v5/final/narration_full.mp4.

### `round4_video_documentary_2026/submission_videos_v4/` (1 dir, 40 MB)
Old videos_v4 directory with 5 demo mp4s + srt/ subdirectory. **This is the flickering
version** (EGL non-deterministic rendering noise) that was replaced by the pure photo
documentary approach in videos_v5. Also removed from GitHub remote via Git Database API
(one commit, 10 files deleted).

### `round4_video_documentary_2026/submission_videos_old/` (1 dir, 10 KB)
Earliest version of submission/videos/ with narration/ and subs/ subdirectories. Superseded.

### `round4_video_documentary_2026/github_repo_mirror/` (1 dir, 975 files, 189 MB)
Old `github_repo/` directory mirror — was a clone of an upstream repo used for reference
during early development. No longer needed since the project has its own structure under
`JCIIOT/` and `submission/`. Archived via robocopy /MOVE (handles .git read-only files).

### `round4_video_documentary_2026/papers_latex_aux/` (7 files, 118 KB)
LaTeX intermediate build products from `papers/bc_debugging_lessons/`:
- `main.aux`, `main.bbl`, `main.blg`, `main.fdb_latexmk`, `main.fls`, `main.log`, `main.out`

Kept in `papers/bc_debugging_lessons/`: `main.pdf` (1049 KB), `main.tex` (4 KB), `references.bib` (6 KB)

### `round4_video_documentary_2026/old_trae_archive_20260719/` (2 dirs, ~152 MB)
Old `.trae/archive/20260719_dsw_bc_training/` directory merged into main archive:
- `debug_logs/` (59 MB) — early DSW BC training debug logs, screenshots, calc_size scripts, fix_hdf5 scripts
- `uploaded_zips/` (94 MB) — `assets_l1_extras.zip`, `assets_l1_minimal.zip`, `jciiot_core.zip` (early DSW upload artifacts)

These were archived on 2026-07-19 during the BC training phase and no longer needed after
skill沉淀 (modelscope-bc-self-train skill preserves the methodology).

### Additional scripts archived by stage413 (2 files)
- `stage412_github_archive.py` — GitHub remote archive script (Git Database API batch delete)
- `stage413_final_archive.py` — this final consolidation script

## Files KEPT in `.trae/temp/` (2 items only)

| File | Purpose |
|------|---------|
| `dsw_remote.py` | DSW remote execution core module (Chrome CDP + JupyterLab API) — required by multiple skills |
| `models_100_100_success/` (6 files) | **100/100 success config backup** — task_config.json, robot_params.json, etc. |

## GitHub Remote Cleanup

- **Deleted**: `submission/videos_v4/*` (10 files: 5 mp4 + 5 srt) via Git Database API
- **Commit**: `249f6505f14ceaad...` — "archive: remove submission/videos_v4/* (flickering version, superseded by videos_v5/final/narration_full.mp4)"
- **Method**: One commit batch delete (sha=null in tree entries), no need to clone
- **Verification**: `submission/videos_v4/` no longer exists on remote

## How to Restore

If any archived file is needed, restore from:
```
d:\APPs\TsinghuaEmbodiedAI\archive\old_interference_2026\round4_video_documentary_2026\<subdir>\
```

### Round 4 subdirectories:
- `temp_scripts/` — stage244-411 Python/PowerShell scripts
- `temp_outputs/` — test audio + competition docs dump
- `submission_videos_v3/` — old videos v3 (722 MB, contains diagnostic PNGs)
- `submission_videos_v4/` — flickering videos v4 (40 MB, also removed from GitHub)
- `submission_videos_old/` — earliest videos version
- `github_repo_mirror/` — old upstream repo mirror (975 files, 189 MB)
- `papers_latex_aux/` — LaTeX intermediate build products

## Archive Statistics (Cumulative)

| Round | Date | Files | Size | Source | Description |
|-------|------|-------|------|--------|-------------|
| 1 | 2026-07-18 | 442 | 40+ MB | `.trae/temp/` (stage1-268) | Initial cleanup |
| 2 | 2026-07-21 | 77 | 2.64 MB | `.trae/temp/` (stage271) + `JCIIOT/` | Post 100/100 cleanup |
| 3 | 2026-07-22 | 411 | ~3 MB | `.trae/temp/` (stage272-310) + `github_repo/JCIIOT/tools/` | Video pipeline cleanup |
| 4 | 2026-07-26 | 1000+ | ~220 MB | `.trae/temp/` + `submission/videos_v3,v4,old` + `github_repo/` + `papers/aux` | Documentary cleanup |
| 4+ | 2026-07-26 | +3 | ~152 MB | `.trae/archive/20260719_dsw_bc_training/` + `stage412/413` scripts | Final consolidation |
| 5 | 2026-08-01 | ~370+ | ~140+ MB | `JCIIOT/tools/_*.py`, `official_repo/`, root briefings, recordings | Upstream-sync housekeeping |
| **Total** | | **2300+** | **~560 MB** | | |

### Round 5 detail (`round5_post_submission_cleanup/`)

See [CLEANUP_MANIFEST.md](./round5_post_submission_cleanup/CLEANUP_MANIFEST.md).

- `jciiot_tools_scratch/` — 350 one-off probe/patch/bisect scripts
- `official_repo_mirror/` — nested JCIIOT2026 clone (prefer `git fetch origin`)
- `competition_briefings/` — teacher pptx/docx/txt from repo root
- `jciiot_recordings_june/` — old 2026-06 FactorySorting1 runtime dumps
- `model_backups/` — `model_epoch_150.pth.bak`
- Also removed empty `.trae-cn/` and 45 `__pycache__/` trees under `JCIIOT/`

## Related
- Final documentary: `submission/videos_v5/final/narration_full.mp4` (2min49s, 26.8MB, 1080p)
- Documentary skill: `c:\Users\52637\.trae-cn\skills\narrative-photo-documentary\`
- Project memory: `c:\Users\52637\.trae-cn\memory\projects\-d-APPs-TsinghuaEmbodiedAI\`
- GitHub remote after cleanup: https://github.com/yigenfeng0707-netizen/TsinghuaEmbodiedAI/tree/main/submission

---

# Archive Update 2026-08-01 (pre-delivery 100/100 objective regen)

Offline objective re-validated at **100/100** (`leaderboard_ref=19`) after FactorySorting
aux_input / station-target hardening and DSW NAS-isolated regen. Delivery sync goes only to
personal GitHub remote `mine` (never competition `origin`).

## Deliverables (tracked on `mine/main`)

| Artifact | Path | Notes |
|----------|------|-------|
| Biendata flat zip | `submission/biendata_validation/SOP-MapGuard_validation_trajectories.zip` | ~577 KB; 5× `L*_FactorySorting*.json` |
| Upload note | `submission/biendata_validation/README_UPLOAD.txt` | last-submission-wins reminder |
| Score snapshot | `submission/trajectories/score_baseline.json` | total 100/100 |
| Agent code | `JCIIOT/src/robot_agent/...`, `robot.py`, `robot_params.json`, regen tool | grasp/transport/backend fixes |

## Local-only round 6 residue

See [round6_pre_delivery_100/README.md](./round6_pre_delivery_100/README.md) — name inventory of
~76 `.trae/temp/_dsw_*` / `_remote_*` / `_sync_*` scratch scripts. Kept gitignored under `.trae/`;
**do not** upload bulk archive blobs (~GB) to GitHub.

## DSW NAS isolation (do not break)

- Work only under `/mnt/workspace/jciiot/` on the shared NAS.
- Never write into GOAI / RoboDojo trees on the same instance.
- Regen + pack skill: `jciiot-dsw-factorysorting-regen`
- GitHub push skill: `github-sync` (SSH remote `mine`)

## Root hygiene

Kept: `JCIIOT/`, `submission/`, `papers/` (local exclude), `archive/` (README only on git),
`ERRATUM.md`, competition docs under `competition description/` (gitignored).
Ignored junk: `JCIIOT/tools/_*.py`, recordings dumps, `__pycache__`, `.trae/`, `*.pth`.

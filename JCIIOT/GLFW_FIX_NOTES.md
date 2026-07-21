# JCIIOT Tiago Transport — GLFW Headless Fix (debug session)

## Root cause of the L1 headless crash
- Symptom: `follow_path` (nav stepping) aborted with native `ERROR: could not initialize GLFW` (glfw/__init__.py:917), no Python traceback, process killed.
- Bisection proved every helper in the nav loop is GL-free; the crash only appeared AFTER `set_physics_grasp_config`/`grasp_object_physics` (which builds a wrapped `EnvRobosuite` eval env using a SECOND osmesa GL context).
- Real cause: the grasp-eval env's MuJoCo/osmesa offscreen GL context lingers after `env.close()` (only freed on `__del__`/gc). The nav env's context (#2) then conflicts with the leaked grasp context (#1) on headless AMD → glfw init aborts.
- Confirmed: a fresh backend (CASE B) or closing the grasp backend before re-creating works. Also `MUJOCO_GL=glfw` is NOT an option — robosuite maps it to EGL which fails on AMD (`Cannot initialize a EGL device display`). Only `osmesa` works.

## Fix (applied to src/robot_agent/environments/robosuite_backend.py on instance)
1. In `grasp_object_physics` (after `_close_wrapped_eval_env`), explicitly free the grasp-eval env's offscreen GL context:
   - `sim._render_context_offscreen.con.free()` then `sim._render_context_offscreen = None` for both `grasp_raw` and `wrapped`, then `gc.collect()`.
2. In `_ensure_physics_policy`, robust checkpoint resolution: try `grasp_policy.checkpoint_path`, then `checkpoint_fallback_path`, then glob `robosuite/robosuite/model_epoch_*.pth`. (Instance robot_params.json points to `model_epoch_500.pth` which does NOT exist; only `model_epoch_150.pth` was trained. The dswhub GET of robot_params showed a `checkpoint_fallback_path` key but `_load_robot_params()` at runtime did NOT see it — stale JupyterHub file cache vs disk discrepancy. Glob fallback sidesteps this.)
3. (Pre-existing, already on instance) `reset()` guards `_set_viewer_camera(render_once=True)` with `if not self._headless`.

## Validation
- Full real path now runs headlessly: `grasp_object_physics(source=...)` executes (prints `[BACKEND] grasp pipeline ...`), then `follow_path(...)` returns `True` with NO GLFW abort.
- Note: grasp itself currently reports `grasp_success=False` (fingerpad contact False, gripper end distance ~7.4 vs target) — BC policy (model_epoch_150.pth, 150 epochs) not reaching object. Separate issue from the crash.

## Remaining issues (NOT yet fixed)
- Grasp quality: BC policy not contacting object. Needs more training / better poses.
- Grasp-site naming: `line_5_container_h01_far_right_grasp_site` (built from task_config.json `grasp_poses`) does not exist in the FactorySorting1 scene; available sites are `..._far_default_site`, `..._near_right_grasp_site`, etc. `task_config.json` `grasp_poses` is EMPTY on the instance — needs populating with correct (source -> site/pos) entries. Valid test sources: `input_1_conveyor_plastic_crate`, `input_3_table_container_h01`, `line_5_container_h01_near`.
- Nav collision: straight path from `[13.5,0]` to `[12.0,0.5]` hits `scene_aabb_proxy_production_line_6` (robot0_base/torso collision). Needs waypoint/path planning around obstacles.

## Env facts (unchanged)
- DSW instance `dsw-2042510`, URL `https://dsw-gateway-cn-hangzhou.data.aliyun.com/dsw-2042510/lab`.
- `MUJOCO_GL=osmesa`, `PYOPENGL_PLATFORM=osmesa` for all runs. xvfb installed but NOT needed (glfw/EGL path fails on AMD).
- Repo at `/mnt/workspace/JCIIOT_repo/JCIIOT`. Checkpoint `robosuite/robosuite/model_epoch_150.pth` (13MB).
- keepalive.py running locally keeps instance alive.

## Sync note
- JupyterHub file API (`c.s.put`/`get`) sometimes serves STALE content. After editing, re-GET and verify the expected string is present before trusting a remote run.

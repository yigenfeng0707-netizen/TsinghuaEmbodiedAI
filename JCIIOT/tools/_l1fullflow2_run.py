import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, traceback as _tb, json, numpy as np
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"
os.environ["GATE_OLLAMA"]="false"; os.environ["GATE_STEP_TIMEOUT"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
def log(*a): print(*a, flush=True)

# Load map + scene context
from robot_agent.core.map_loader import load_map_files
from robot_agent.core.scene_context import SceneContext
map_dir = P(APP) / "robosuite" / "robosuite" / "environments" / "factory_sorting" / "generated_maps"
semantic = map_dir / "factory_sorting_1_3fo3erfhisem_scene_regenerated_semantic_map.json"
grid_file = map_dir / "factory_sorting_1_3fo3erfhisem_scene_regenerated_occupancy_grid.npy"
if not semantic.exists():
    semantic = map_dir / "factory_sorting_scene_regenerated_semantic_map.json"
    grid_file = map_dir / "factory_sorting_scene_regenerated_occupancy_grid.npy"
log("semantic map:", semantic.name, "exists:", semantic.exists())
scene, grid = load_map_files(semantic, grid_file)
scene_ctx = SceneContext.from_semantic_map(scene)
log("scene context loaded")

# Build backend (single reset, avoid _build_agent double-reset GLFW issue)
from robot_agent.environments import RobosuiteBackend
cfg = json.load(open(P(APP)/"knowledge"/"task_config.json"))
task = next(t for t in cfg["tasks"] if t["level"]=="L1")
backend = RobosuiteBackend(env_name=task["env_name"], camera="birdview", headless=True, drive_mode="direct")
backend._scene_context = scene_ctx
backend.reset()
log("backend reset ok")

# object map
objs = tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"], {})
backend.set_physics_grasp_config(device="cpu", object_map=objs)
log("physics grasp config set")

# Run L1 via ChampionTransportFlow
from robot_agent.workflows.champion_transport import ChampionTransportFlow
flow = ChampionTransportFlow(
    backend=backend,
    scene_context=scene_ctx,
    grid=grid,
    task_config_path=str(P(APP)/"knowledge"/"task_config.json"),
)
log("flow built, running L1...")
try:
    report = flow.execute_level("L1")
    log("=== L1 RESULT ===")
    log("success:", report.success)
    log("failed_step:", report.failed_step)
    for s in report.steps:
        log("  step:", s.skill_name, "ok:", s.success, (s.message or "")[:100])
except Exception as e:
    log("L1 FAIL:", repr(e)[:300])
    log(_tb.format_exc()[-1500:])

# final object pos
env = backend.env
for jn in env.sim.model.joint_names:
    if task["object"] in jn and ("_free" in jn or "_joint0" in jn):
        qpos = env.sim.data.get_joint_qpos(jn)
        log("final object pos:", qpos.tolist()[:3])
        break
backend.close()
log("DONE")
'''

c = d.Dswhub()
c.s.put(d.BASE+"/api/contents/_l1fullflow2.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_l1fullflow2.py'],stdout=open('/mnt/workspace/_l1fullflow2.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

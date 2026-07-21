import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, json, numpy as np, traceback as _tb
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"
os.environ["GATE_OLLAMA"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
def log(*a): print(*a, flush=True)

from robot_agent.core.map_loader import load_map_files
from robot_agent.core.scene_context import SceneContext
from robot_agent.environments import RobosuiteBackend
from robot_agent.workflows.champion_transport import ChampionTransportFlow

cfg = json.load(open(P(APP)/"knowledge"/"task_config.json"))
map_dir = P(APP) / "robosuite" / "robosuite" / "environments" / "factory_sorting" / "generated_maps"
lvl="L4"
task = next(t for t in cfg["tasks"] if t["level"]==lvl)
prefix="factory_sorting_7_3fo3erfky9rn"
semantic = map_dir / f"{prefix}_scene_regenerated_semantic_map.json"
grid_file = map_dir / f"{prefix}_scene_regenerated_occupancy_grid.npy"
scene, grid = load_map_files(semantic, grid_file)
scene_ctx = SceneContext.from_semantic_map(scene)
backend = RobosuiteBackend(env_name=task["env_name"], camera="birdview", headless=True, drive_mode="direct")
backend._scene_context = scene_ctx
backend.reset()
objs = tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"], {})
backend.set_physics_grasp_config(device="cpu", object_map=objs)
flow = ChampionTransportFlow(backend=backend, scene_context=scene_ctx, grid=grid, task_config_path=str(P(APP)/"knowledge"/"task_config.json"))
log(f"running {lvl}...")
try:
    report = flow.execute_level(lvl)
    log(f"success={report.success} failed_step={report.failed_step}")
    for s in report.steps:
        log(f"  {s.skill_name}: {'OK' if s.success else 'FAIL'}")
    env = backend.env
    for jn in env.sim.model.joint_names:
        if task["object"] in jn and ("_free" in jn or "_joint0" in jn):
            log(f"final object pos: {env.sim.data.get_joint_qpos(jn).tolist()[:3]}")
            break
except Exception as e:
    log(f"FAIL: {repr(e)[:200]}")
    log(_tb.format_exc()[-800:])
backend.close()
log("DONE")
'''

c = d.Dswhub()
c.s.put(d.BASE+"/api/contents/_l4_only.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_l4_only.py'],stdout=open('/mnt/workspace/_l4_only.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

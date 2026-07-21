import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, traceback as _tb, json
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"; os.environ["GATE_OLLAMA"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
def log(*a): print(*a, flush=True)
import numpy as _np
from robot_agent.environments import RobosuiteBackend
cfg=json.load(open(APP+"/knowledge/task_config.json"))
task=next(t for t in cfg["tasks"] if t["level"]=="L1")
gp=cfg["grasp_poses"][task["source"]]
ckpt="/mnt/workspace/JCIIOT_repo/JCIIOT/bc_trained_models/l1_run_v2/l1_bc_lordim_v2/20260718161523/models/model_epoch_300.pth"
log("using checkpoint:", ckpt)
backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
objs=tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"],{})
backend.set_physics_grasp_config(checkpoint=ckpt, device="cpu", object_map=objs)
backend.reset(); log("reset ok")
ibp={"xy":gp["pos"][:2],"yaw":gp["yaw"]}
try:
    ok=backend.grasp_object_physics(source=task["source"], object_name=task["object"], initial_base_pose=ibp)
    log("grasp ok=", ok)
except Exception as e:
    log("grasp FAIL", repr(e)[:200])
try:
    env=backend.env
    for jn in env.sim.model.joint_names:
        if task["object"] in jn and ("_free" in jn or "_joint0" in jn):
            log("object pos:", env.sim.data.get_joint_qpos(jn).tolist()[:3]); break
except: pass
backend.close(); log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_l1picktest300.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_l1picktest300.py'],stdout=open('/mnt/workspace/_l1picktest300.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

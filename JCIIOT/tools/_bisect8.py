import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, traceback as _tb
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"; os.environ["GATE_OLLAMA"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
# monkeypatch glfw.init to print stack
import glfw as _glfw
_orig_init=_glfw.init
def _patched_init():
    print("[GLFW.init] called from:", "".join(_tb.format_stack()[-6:]), flush=True)
    return _orig_init()
_glfw.init=_patched_init
import glfw; glfw.init=_patched_init
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
def log(*a): print(*a, flush=True)
import numpy as _np
from robot_agent.environments import RobosuiteBackend
backend=RobosuiteBackend(env_name="FactorySorting1_3FO3ERFHISEM",camera="birdview",headless=True,drive_mode="direct")
objs=tsr.SCENE_INPUT_OBJECT_MAP.get("FactorySorting1_3FO3ERFHISEM",{})
log("== calling set_physics_grasp_config ==")
backend.set_physics_grasp_config(device="cpu",object_map=objs)
backend.reset(); log("reset2 ok")
log("== calling follow_path ==")
xy,yaw=backend.get_base_pose()
res=backend.follow_path([_np.array(xy)], max_steps=50, record_every=0)
log("follow_path res", res)
backend.close(); log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_bisect8.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_bisect8.py'],stdout=open('/mnt/workspace/_bisect8.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=60))

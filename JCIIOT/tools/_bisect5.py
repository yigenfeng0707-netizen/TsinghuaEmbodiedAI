import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

PATCH = r'''
import re
p="/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py"
s=open(p).read()
# add a print at entry of _follow_path_direct and before env.render in direct
marker="    robot = env.robots[0]\n    waypoint_index = 0"
if "MARKER_ENTER_FOLLOW_DIRECT" not in s:
    s=s.replace(marker, '    print("[FOLLOW_DIRECT] ENTER headless="+str(headless), flush=True)\n'+marker,1)
# instrument _get_base_pose call
s=s.replace("        base_xy, _ = _get_base_pose(env)\n","        print(\"[FOLLOW_DIRECT] step top\", flush=True)\n        base_xy, _ = _get_base_pose(env)\n",1)
s=s.replace("        _set_base_xy_direct(env, robot, step_xy)\n","        print(\"[FOLLOW_DIRECT] before set_base\", flush=True)\n        _set_base_xy_direct(env, robot, step_xy)\n",1)
s=s.replace("        env.step(idle_action)\n","        print(\"[FOLLOW_DIRECT] before step\", flush=True)\n        env.step(idle_action)\n        print(\"[FOLLOW_DIRECT] after step\", flush=True)\n",1)
open(p,"w").write(s)
print("patched")
'''

INNER = r'''
import os, sys, importlib.util, traceback as _tb
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
backend=RobosuiteBackend(env_name="FactorySorting1_3FO3ERFHISEM",camera="birdview",headless=True,drive_mode="direct")
dyn={}
for pn,on in backend._load_objects() if hasattr(backend,"_load_objects") else []:
    pass
objs=tsr.SCENE_INPUT_OBJECT_MAP.get("FactorySorting1_3FO3ERFHISEM",{})
backend.set_physics_grasp_config(device="cpu",object_map=objs)
backend.reset(); log("reset2 ok")
start_xy,start_yaw=backend.get_base_pose()
log("base pose", start_xy.tolist())
path=[_np.array(start_xy)]
res=backend.follow_path(path, max_steps=50, record_every=0)
log("follow_path trivial res", res)
backend.close(); log("DONE")
'''

c=d.Dswhub()
# apply patch
print(c.run_python(PATCH, timeout=60))
# upload inner
c.s.put(d.BASE+"/api/contents/_bisect5.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_bisect5.py'],stdout=open('/mnt/workspace/_bisect5.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=60))

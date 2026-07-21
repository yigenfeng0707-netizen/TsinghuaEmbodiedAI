import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, traceback as _tb
os.environ["MUJOCO_GL"]="glfw"; os.environ.pop("PYOPENGL_PLATFORM",None); os.environ["GATE_OLLAMA"]="false"
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
objs=tsr.SCENE_INPUT_OBJECT_MAP.get("FactorySorting1_3FO3ERFHISEM",{})
backend.set_physics_grasp_config(device="cpu",object_map=objs)
backend.reset(); log("reset2 ok")
xy,yaw=backend.get_base_pose(); log("base pose", xy.tolist())
try:
    res=backend.follow_path([_np.array(xy)], max_steps=50, record_every=0)
    log("follow_path res", res)
except Exception as e:
    log("follow_path FAIL", repr(e)); log(_tb.format_exc())
backend.close(); log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_xvfb_test.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'glfw','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['xvfb-run','-a','-s','-screen 0 1024x768x24','python','/mnt/workspace/_xvfb_test.py'],stdout=open('/mnt/workspace/_xvfb_test.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=60))

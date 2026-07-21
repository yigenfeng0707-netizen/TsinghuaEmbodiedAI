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
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
def log(*a): print(*a, flush=True)
import numpy as _np
from robot_agent.environments import RobosuiteBackend
backend=RobosuiteBackend(env_name="FactorySorting1_3FO3ERFHISEM",camera="birdview",headless=True,drive_mode="direct")
backend.reset(); log("reset ok")
env=backend.env
idle=_np.zeros_like(env.action_spec[0])
log("capture_frame...")
img=backend.capture_frame(); log("capture OK", img.shape)
log("step after capture...")
env.step(idle); log("step-after-capture OK")
# now disable offscreen and try
log("disabling offscreen, capture then step...")
env.has_offscreen_renderer=False
img2=backend.capture_frame(); log("capture with offscreen off FAIL? shape", None if img2 is None else img2.shape)
backend.close(); log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_bisect4.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_bisect4.py'],stdout=open('/mnt/workspace/_bisect4.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=60))

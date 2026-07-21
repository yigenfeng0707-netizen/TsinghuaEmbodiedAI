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
from robot_agent.environments import RobosuiteBackend
backend=RobosuiteBackend(env_name="FactorySorting1_3FO3ERFHISEM",camera="birdview",headless=True,drive_mode="direct")
backend.reset(); log("reset ok")
import numpy as _np
idle=_np.zeros_like(backend.env.action_spec[0])
try:
    log("stepping 1...")
    backend.env.step(idle); log("step1 OK")
except Exception as e:
    log("step FAIL:", repr(e)); log(_tb.format_exc())
# try disabling offscreen on the env and step
try:
    backend.env.has_offscreen_renderer=False
    log("stepping with offscreen disabled...")
    backend.env.step(idle); log("step2 OK (offscreen off)")
except Exception as e:
    log("step2 FAIL:", repr(e))
backend.close(); log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_bisect2.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
code = (
    "import subprocess,os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
    "p=subprocess.Popen(['python','/mnt/workspace/_bisect2.py'],stdout=open('/mnt/workspace/_bisect2.log','w'),stderr=subprocess.STDOUT,env=env)\n"
    "print('LAUNCHED',p.pid)\n"
)
print(c.run_python(code, timeout=60))

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
import robot_agent.environments.robosuite_backend as RB
backend=RobosuiteBackend(env_name="FactorySorting1_3FO3ERFHISEM",camera="birdview",headless=True,drive_mode="direct")
backend.reset(); log("reset ok")
env=backend.env
robot=env.robots[0]
idle=_np.zeros_like(env.action_spec[0])
posture=RB._capture_upper_body_posture(env, robot); log("capture posture OK")
# replicate loop manually
log("set_base_xy_direct...")
RB._set_base_xy_direct(env, robot, _np.array([13.5,0.0]))
log("try_sync_transport...")
RB._try_sync_transport(env)
log("step...")
env.step(idle)
log("restore posture...")
RB._restore_upper_body_posture(env, posture)
log("try_sync_transport2...")
RB._try_sync_transport(env)
log("collision check...")
c=RB._should_stop_for_collision(env, robot, [], 0, 5, 100); log("collision:", c)
log("ALL HELPERS OK -> the loop body is GL-free; crash must be elsewhere")
backend.close(); log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_bisect3.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
code = (
    "import subprocess,os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
    "p=subprocess.Popen(['python','/mnt/workspace/_bisect3.py'],stdout=open('/mnt/workspace/_bisect3.log','w'),stderr=subprocess.STDOUT,env=env)\n"
    "print('LAUNCHED',p.pid)\n"
)
print(c.run_python(code, timeout=60))

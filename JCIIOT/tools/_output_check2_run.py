import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, json
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

from robot_agent.environments import RobosuiteBackend
cfg=json.load(open(P(APP)/"knowledge"/"task_config.json"))
for lvl in ["L1","L2","L3","L4","L5"]:
    task=next(t for t in cfg["tasks"] if t["level"]==lvl)
    backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
    backend.reset()
    env=backend.env
    op=getattr(env,"output_ports",{})
    log(f"{lvl} target={task['target']} output_ports={list(op.keys())}")
    backend.close()
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_output_check2.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_output_check2.py'],stdout=open('/mnt/workspace/_output_check2.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

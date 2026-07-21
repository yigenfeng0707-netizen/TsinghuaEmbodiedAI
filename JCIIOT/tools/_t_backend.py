import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, json, importlib.util
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"; os.environ["GATE_OLLAMA"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
print("STEP1 imports ok")
from robot_agent.environments import RobosuiteBackend
print("STEP2 RobosuiteBackend imported")
b=RobosuiteBackend(env_name="FactorySorting1_3FO3ERFHISEM",camera="birdview",headless=True,drive_mode="direct")
print("STEP3 backend constructed")
b.reset()
print("STEP4 reset ok")
b.close()
print("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_t_backend.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nenv={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\nr=subprocess.run(['python','/mnt/workspace/_t_backend.py'],stdout=open('/mnt/workspace/_t_backend.out','w'),stderr=subprocess.STDOUT,timeout=300,env=env)\nprint('EXIT',r.returncode)\nprint(open('/mnt/workspace/_t_backend.out').read()[-2500:])", timeout=360))

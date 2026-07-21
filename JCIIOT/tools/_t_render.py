import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"; os.environ["GATE_OLLAMA"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
print("MUJOCO_GL=",os.environ.get("MUJOCO_GL"))
import mujoco
print("mujoco", mujoco.__version__)
from robot_agent.environments import RobosuiteBackend
b=RobosuiteBackend(env_name="FactorySorting1_3FO3ERFHISEM",camera="birdview",headless=True,drive_mode="direct")
b.reset()
print("nav reset ok; offscreen render test")
try:
    img=b.env.sim.render(camera_name="birdview",height=64,width=64,depth=False)
    print("RENDER OK", None if img is None else getattr(img,'shape',type(img)))
except Exception as e:
    import traceback; traceback.print_exc()
b.close(); print("DONE")
'''
c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_t_render.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nenv={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\nr=subprocess.run(['python','/mnt/workspace/_t_render.py'],stdout=open('/mnt/workspace/_t_render.out','w'),stderr=subprocess.STDOUT,timeout=200,env=env)\nprint('EXIT',r.returncode)\nprint(open('/mnt/workspace/_t_render.out').read()[-2000:])", timeout=260))

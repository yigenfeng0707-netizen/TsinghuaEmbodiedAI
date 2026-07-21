import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, json, importlib.util, traceback as _tb
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"; os.environ["GATE_OLLAMA"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
def log(*a): print(*a, flush=True)
from robot_agent.core.map_loader import load_map_files
from robot_agent.core.scene_context import SceneContext
from robot_agent.environments import RobosuiteBackend
app_dir=P(APP); env_name=tsr._scene_env_name(0)
semantic,grid_file=tsr._choose_map_files(app_dir,0)
scene,grid=load_map_files(semantic,grid_file)
scene_ctx=SceneContext.from_semantic_map(scene)
backend=RobosuiteBackend(env_name=env_name,camera="birdview",headless=True,drive_mode="direct")
backend._scene_context=scene_ctx
backend.reset(); log("reset1 ok")
raw=getattr(backend.env,"material_metadata",{}) or {}
dyn={}
for on,info in raw.items():
    if not isinstance(info,dict): continue
    pn=str(info.get("port_name") or "")
    if pn:
        dyn[pn]=on
        if pn.startswith("input_"): dyn["line_"+pn.split("_",1)[1]]=on
        elif pn.startswith("line_"): dyn["input_"+pn.split("_",1)[1]]=on
full=dict(dyn); full.update(tsr.SCENE_INPUT_OBJECT_MAP.get(env_name,{}))
backend.set_physics_grasp_config(device="cpu",object_map=full)
backend.reset(); log("reset2 ok")
# TEST1: capture_frame directly on nav env
try:
    img=backend.capture_frame(camera="birdview")
    log("capture_frame OK", None if img is None else img.shape)
except Exception as e:
    log("capture_frame FAIL:", repr(e)); log(_tb.format_exc())
# TEST2: follow_path to a trivial nearby point (short)
try:
    import numpy as _np
    start_xy,start_yaw=backend.get_base_pose()
    log("base pose", start_xy.tolist(), float(start_yaw))
    path=[_np.array(start_xy)]
    res=backend.follow_path(path, max_steps=50, record_every=0)
    log("follow_path trivial res", res)
except Exception as e:
    log("follow_path FAIL:", repr(e)); log(_tb.format_exc())
backend.close(); log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_bisect.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
code = (
    "import subprocess,os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
    "p=subprocess.Popen(['python','/mnt/workspace/_bisect.py'],stdout=open('/mnt/workspace/_bisect.log','w'),stderr=subprocess.STDOUT,env=env)\n"
    "print('LAUNCHED',p.pid)\n"
)
print(c.run_python(code, timeout=60))

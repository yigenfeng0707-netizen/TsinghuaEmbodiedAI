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
# Patch make_eval_env to disable offscreen rendering when headless (no GL context for grasp env)
import robot_agent.environments.robosuite_backend as RB
_orig_make=RB.load_factory_sorting_evalization.make_eval_env if hasattr(RB,"load_factory_sorting_evalization") else None
import importlib
ev=importlib.import_module("robosuite.environments.factory_sorting.load_factory_sorting_evalization")
_real_make=ev.make_eval_env
def _patched_make(args, config, ckpt_dict, render):
    env=_real_make(args, config, ckpt_dict, render)
    # strip offscreen GL context for headless grasp eval
    try:
        if hasattr(env,"env") and hasattr(env.env,"sim"):
            env.env.has_offscreen_renderer=False
        env.has_offscreen_renderer=False
    except Exception as e:
        print("patch err", e, flush=True)
    return env
ev.make_eval_env=_patched_make
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
xy,yaw=backend.get_base_pose()
try:
    res=backend.follow_path([_np.array(xy)], max_steps=50, record_every=0)
    log("follow_path res", res)
except Exception as e:
    log("follow_path FAIL", repr(e))
backend.close(); log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_bisect10.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_bisect10.py'],stdout=open('/mnt/workspace/_bisect10.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=60))

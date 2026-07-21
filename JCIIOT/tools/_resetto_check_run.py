import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, json
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"; os.environ["GATE_OLLAMA"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
import numpy as np, argparse
from robot_agent.environments import RobosuiteBackend
backend=RobosuiteBackend(env_name="FactorySorting1_3FO3ERFHISEM",camera="birdview",headless=True,drive_mode="direct")
objs=tsr.SCENE_INPUT_OBJECT_MAP.get("FactorySorting1_3FO3ERFHISEM",{})
backend.set_physics_grasp_config(device="cpu",object_map=objs)
backend.reset()
# build wrapped env like grasp_object_physics does
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env
gp=backend._physics_config
ck=backend._physics_ckpt_dict
ns=argparse.Namespace(factory_scene="FactorySorting1_3FO3ERFHISEM",robot_base_pos=[8.0,4.6,0.0],robot_base_ori=[0,0,-3.14],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
wrapped=make_eval_env(ns,config=gp,ckpt_dict=ck,render=False)
print("wrapped type:", type(wrapped).__name__)
print("has reset_to:", hasattr(wrapped,"reset_to"))
print("has reset:", hasattr(wrapped,"reset"))
import inspect
if hasattr(wrapped,"reset_to"):
    print("reset_to sig:", inspect.signature(wrapped.reset_to))
if hasattr(wrapped,"reset"):
    print("reset sig:", inspect.signature(wrapped.reset))
# check reset options
print("wrapped methods:", [m for m in dir(wrapped) if 'reset' in m.lower() or 'state' in m.lower()][:15])
# demo metadata
import h5py
f=h5py.File("/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5","r")
print("data attrs:", dict(f["data"].attrs) if len(f["data"].attrs)<15 else list(f["data"].attrs.keys()))
print("env_meta:", f["data"].attrs.get("env_metadata",{}))
f.close()
backend.close()
print("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_resetto_check.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_resetto_check.py'],stdout=open('/mnt/workspace/_resetto_check.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

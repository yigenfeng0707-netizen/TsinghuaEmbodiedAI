import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, json, numpy as np, argparse
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

import importlib
col = importlib.import_module("robosuite.environments.factory_sorting.load_factory_sorting_1_3fo3erfhisem_collect")
from robot_agent.environments import RobosuiteBackend
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env, object_grasp_site_name

cfg=json.load(open(P(APP)/"knowledge"/"task_config.json"))
task=next(t for t in cfg["tasks"] if t["level"]=="L2")
obj_name=task["object"]
backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
objs=tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"],{})
backend.set_physics_grasp_config(device="cpu",object_map=objs)
backend.reset()
ns=argparse.Namespace(factory_scene=task["env_name"],robot_base_pos=[0,0,0],robot_base_ori=[0,0,-3.14],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
wrapped=make_eval_env(ns,config=backend._physics_config,ckpt_dict=backend._physics_ckpt_dict,render=False)
wrapped.reset()
raw=base_robosuite_env(wrapped)
raw.sim.forward()

# grasp sites
for arm in ["right","left"]:
    sn=object_grasp_site_name(obj_name, arm)
    sid=raw.sim.model.site_name2id(sn)
    log(f"grasp site {arm}: {raw.sim.data.site_xpos[sid].tolist()}")

# object collision geoms positions
geoms=col.object_collision_geoms(raw, obj_name)
log(f"collision geoms: {geoms}")
for g in geoms[:6]:
    gid=raw.sim.model.geom_name2id(g)
    log(f"  {g}: pos={raw.sim.data.geom_xpos[gid].tolist()} size={raw.sim.model.geom_size[gid].tolist()[:3]}")

# all sites of object
log("all sites:")
for i in range(raw.sim.model.nsite):
    sn=raw.sim.model.site_id2name(i)
    if obj_name in sn:
        log(f"  {sn}: {raw.sim.data.site_xpos[i].tolist()}")

# object joint pos
for jn in raw.sim.model.joint_names:
    if obj_name in jn:
        log(f"joint {jn}: qpos={raw.sim.data.get_joint_qpos(jn).tolist()[:3]}")
        break
backend.close()
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_tote_geom.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_tote_geom.py'],stdout=open('/mnt/workspace/_tote_geom.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

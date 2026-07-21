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
col.append_current_obs = lambda base_env, obs_buffer: None
from robot_agent.environments import RobosuiteBackend
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env, print_grasp_debug_info
import robot_agent.environments.robosuite_backend as RB

cfg=json.load(open(P(APP)/"knowledge"/"task_config.json"))
# L1 container: check contact mechanism
task=next(t for t in cfg["tasks"] if t["level"]=="L1")
gp=cfg["grasp_poses_by_level"]["L1"]
obj_name=task["object"]
log(f"L1 container base={gp['pos']} obj={obj_name}")

backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
objs=tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"],{})
backend.set_physics_grasp_config(device="cpu",object_map=objs)
backend.reset()
ns=argparse.Namespace(factory_scene=task["env_name"],robot_base_pos=gp["pos"],robot_base_ori=[0,0,gp["yaw"]],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
wrapped=make_eval_env(ns,config=backend._physics_config,ckpt_dict=backend._physics_ckpt_dict,render=False)
wrapped.reset()
raw=base_robosuite_env(wrapped)
raw.sim.forward()
robot=raw.robots[0]

# run scripted grasp
result = RB._scripted_grasp_in_wrapped_env(wrapped, raw, obj_name, headless=True, render_callback=None)
log(f"L1 grasp: {result}")

# fingerpad contact pairs (which geoms touch)
_, grasps = print_grasp_debug_info(raw, robot, obj_name, col.get_target_positions(raw, obj_name, 0.035)[0], label="L1 after grasp")
log(f"L1 grasps: {grasps}")

# eef positions and object geoms
below_targets,_=col.get_target_positions(raw, obj_name, 0.035)
for arm in col.ARMS:
    ep=col.get_eef_pos(raw, robot, arm)
    log(f"  L1 eef {arm}: {ep.tolist()} target {below_targets[arm].tolist()} dist {np.linalg.norm(ep-below_targets[arm]):.3f}")

# object collision geoms
geoms=col.object_collision_geoms(raw, obj_name)
log(f"L1 obj geoms: {geoms}")
for g in geoms[:6]:
    gid=raw.sim.model.geom_name2id(g)
    log(f"  {g}: pos={raw.sim.data.geom_xpos[gid].tolist()} size={raw.sim.model.geom_size[gid].tolist()[:3]}")
backend.close()
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_l1_contact.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_l1_contact.py'],stdout=open('/mnt/workspace/_l1_contact.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

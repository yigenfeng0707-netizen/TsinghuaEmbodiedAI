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
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env, object_grasp_site_name

cfg=json.load(open(P(APP)/"knowledge"/"task_config.json"))
# Try approach from +y direction (yaw=-pi/2 facing -y) for tote levels
# base = grasp_mid + [0, +0.8] (behind in +y), yaw=-1.57
for lvl in ["L2","L3","L5"]:
    task=next(t for t in cfg["tasks"] if t["level"]==lvl)
    obj_name=task["object"]
    # get grasp_mid
    backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
    objs=tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"],{})
    backend.set_physics_grasp_config(device="cpu",object_map=objs)
    backend.reset()
    ns=argparse.Namespace(factory_scene=task["env_name"],robot_base_pos=[0,0,0],robot_base_ori=[0,0,-3.14],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
    wrapped=make_eval_env(ns,config=backend._physics_config,ckpt_dict=backend._physics_ckpt_dict,render=False)
    wrapped.reset()
    raw=base_robosuite_env(wrapped)
    raw.sim.forward()
    rsite=raw.sim.data.site_xpos[raw.sim.model.site_name2id(object_grasp_site_name(obj_name,"right"))]
    lsite=raw.sim.data.site_xpos[raw.sim.model.site_name2id(object_grasp_site_name(obj_name,"left"))]
    grasp_mid=np.array([(rsite[0]+lsite[0])/2, (rsite[1]+lsite[1])/2])
    backend.close()
    # try yaw=-pi/2, base at grasp_mid + [0, +0.8]
    yaw=-1.5708
    base_pos=[grasp_mid[0], grasp_mid[1]+0.8, 0.0]
    backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
    backend.set_physics_grasp_config(device="cpu",object_map=objs)
    backend.reset()
    ns2=argparse.Namespace(factory_scene=task["env_name"],robot_base_pos=base_pos,robot_base_ori=[0,0,yaw],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
    w2=make_eval_env(ns2,config=backend._physics_config,ckpt_dict=backend._physics_ckpt_dict,render=False)
    w2.reset()
    r2=base_robosuite_env(w2)
    r2.sim.forward()
    robot=r2.robots[0]
    starts={arm: col.get_eef_pos(r2, robot, arm) for arm in col.ARMS}
    below_targets,_=col.get_target_positions(r2, obj_name, 0.035)
    touch=col.gripper_touches_object(r2, robot, obj_name)
    right_dist=np.linalg.norm(starts["right"][:2]-below_targets["right"][:2])
    left_dist=np.linalg.norm(starts["left"][:2]-below_targets["left"][:2])
    log(f"{lvl} yaw=-pi/2 base=[{base_pos[0]:.2f},{base_pos[1]:.2f}]: touch={touch} R_dist={right_dist:.3f} L_dist={left_dist:.3f}")
    log(f"  starts R={starts['right'].tolist()} L={starts['left'].tolist()}")
    log(f"  targets R={below_targets['right'].tolist()} L={below_targets['left'].tolist()}")
    backend.close()
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_yaw_test.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_yaw_test.py'],stdout=open('/mnt/workspace/_yaw_test.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

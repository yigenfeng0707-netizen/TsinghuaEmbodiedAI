import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, json, numpy as np, h5py
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"; os.environ["GATE_OLLAMA"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
from robot_agent.environments import RobosuiteBackend
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env, current_wrapped_policy_obs
import argparse

cfg=json.load(open(APP+"/knowledge/task_config.json"))
task=next(t for t in cfg["tasks"] if t["level"]=="L1")
gp=cfg["grasp_poses"][task["source"]]
ckpt="/mnt/workspace/JCIIOT_repo/JCIIOT/bc_trained_models/l1_run_v2/l1_bc_lordim_v2/20260718161523/models/model_epoch_300.pth"

backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
objs=tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"],{})
backend.set_physics_grasp_config(checkpoint=ckpt, device="cpu", object_map=objs)
backend.reset()

# build wrapped env
ns=argparse.Namespace(factory_scene=task["env_name"],robot_base_pos=gp["pos"],robot_base_ori=[0,0,gp["yaw"]],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
wrapped=make_eval_env(ns,config=backend._physics_config,ckpt_dict=backend._physics_ckpt_dict,render=False)
raw=base_robosuite_env(wrapped)

# demo obs[0]
f=h5py.File("/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5","r")
dk=list(f["data"].keys())[0]
demo_obs=f["data"][dk]["obs"]
demo_acts=f["data"][dk]["actions"]
print("=== DEMO obs[0] ===")
for k in ["robot0_right_eef_pos","robot0_left_eef_pos","robot0_right_eef_quat","robot0_right_gripper_qpos"]:
    if k in demo_obs:
        print(f"  {k}: {demo_obs[k][0]}")
print("=== DEMO actions[0:3] ===")
print(demo_acts[:3])
_acts_np=np.array(demo_acts)
print("=== DEMO actions stats (per dim) ===")
print("mean:", _acts_np.mean(axis=0).round(3))
print("std:", _acts_np.std(axis=0).round(3))
f.close()

# reset_to demo state
states=np.array(h5py.File("/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5","r")["data"][dk]["states"][0])
wrapped.reset_to(states)

# eval obs after reset_to
eval_obs=current_wrapped_policy_obs(wrapped)
print("=== EVAL obs after reset_to ===")
for k in ["robot0_right_eef_pos","robot0_left_eef_pos","robot0_right_eef_quat","robot0_right_gripper_qpos"]:
    if k in eval_obs:
        print(f"  {k}: {np.asarray(eval_obs[k]).round(4)}")

# run policy 1 step and check action
policy=backend._physics_policy
policy.start_episode()
act=np.asarray(policy(ob=eval_obs),dtype=float).reshape(-1)
print("=== POLICY action[0] ===")
print("action:", act.round(4), "shape:", act.shape)
print("demo action[0]:", demo_acts[0].round(4))

backend.close()
print("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_obsdiag.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_obsdiag.py'],stdout=open('/mnt/workspace/_obsdiag.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

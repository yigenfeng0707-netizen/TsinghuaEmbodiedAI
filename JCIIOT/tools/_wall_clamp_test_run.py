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
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env, grasp_status, print_grasp_debug_info

cfg=json.load(open(P(APP)/"knowledge"/"task_config.json"))
task=next(t for t in cfg["tasks"] if t["level"]=="L2")
obj_name=task["object"]
# base in +x, yaw=-pi (face -x). eef starts ~0.37 in front of base (-x dir)
# To clamp right wall (x=12.168) from outside, base must be at x>12.168+0.37=12.54
# But then left arm cant reach left wall. Try: only clamp right wall (single arm).
# base at [12.6, 4.625] (aligned with object y center), yaw=-pi
base_pos=[12.6, 4.625, 0.0]
yaw=-3.14
log(f"L2 single-arm test base={base_pos}")

backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
objs=tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"],{})
backend.set_physics_grasp_config(device="cpu",object_map=objs)
backend.reset()
ns=argparse.Namespace(factory_scene=task["env_name"],robot_base_pos=base_pos,robot_base_ori=[0,0,yaw],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
wrapped=make_eval_env(ns,config=backend._physics_config,ckpt_dict=backend._physics_ckpt_dict,render=False)
wrapped.reset()
raw=base_robosuite_env(wrapped)
raw.sim.forward()
robot=raw.robots[0]

# right wall outer: x=12.168, y=4.625, z=1.2
# eef start
starts={arm: col.get_eef_pos(raw, robot, arm) for arm in col.ARMS}
log(f"starts: R={starts['right'].tolist()} L={starts['left'].tolist()}")

# move right arm to right wall outer (x=12.17, y=4.625, z=1.2), left stays
# use step_towards_targets
args=argparse.Namespace(site_below_offset=0.035,show_object_sites=False,object_site_size=0.04,camera="robot0_robotview",render_sleep=0.0,up_steps=50,xy_steps=80,down_steps=50,safe_z=0.10,site_above_clearance=0.15,arrival_tolerance=0.15,gripper_end_arrival_tolerance=0.15,settle_steps=100,grasp_steps=40,max_action=0.65,initial_view_steps=15)

# target: right eef at [12.17, 4.625, 1.2] (right wall outer), left eef at [11.57, 4.625, 1.2] (left wall outer)
targets={"right": np.array([12.155, 4.625, 1.2]), "left": np.array([11.585, 4.625, 1.2])}
class DB: pass
# move up first
safe_t={a: np.array([starts[a][0], starts[a][1], 1.5]) for a in col.ARMS}
ok,_=col.move_along_linear_segment(wrapped, raw, robot, obj_name, safe_t, 50, -1.0, False, args, DB(), reject_object_contact=False, label="up")
log(f"up: {ok}")
# move to wall targets
ok,reason=col.move_along_linear_segment(wrapped, raw, robot, obj_name, targets, 80, -1.0, False, args, DB(), reject_object_contact=False, label="wall-approach")
log(f"wall-approach: {ok} {reason[:80] if reason else ''}")
# close grippers
for _ in range(40):
    action=col.build_action(raw, robot, {}, gripper_value=-1.0)
    wrapped.step(action)
_, grasps = print_grasp_debug_info(raw, robot, obj_name, targets, label="after wall clamp")
log(f"grasps: {grasps}")
for arm in col.ARMS:
    log(f"  eef {arm}: {col.get_eef_pos(raw, robot, arm).tolist()}")
backend.close()
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_wall_clamp_test.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_wall_clamp_test.py'],stdout=open('/mnt/workspace/_wall_clamp_test.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, json, numpy as np, argparse, traceback as _tb
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"; os.environ["GATE_OLLAMA"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
from robot_agent.environments import RobosuiteBackend
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env, grasp_status, print_grasp_debug_info

# import scripted grasp functions from collect script
import importlib
col = importlib.import_module("robosuite.environments.factory_sorting.load_factory_sorting_1_3fo3erfhisem_collect")
col.append_current_obs = lambda base_env, obs_buffer: None

cfg=json.load(open(APP+"/knowledge/task_config.json"))
task=next(t for t in cfg["tasks"] if t["level"]=="L1")
gp=cfg["grasp_poses"][task["source"]]
obj_name=task["object"]
print("L1 object:", obj_name, "base:", gp["pos"], "yaw:", gp["yaw"])

backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
objs=tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"],{})
backend.set_physics_grasp_config(device="cpu",object_map=objs)
backend.reset()

# build wrapped env
ns=argparse.Namespace(factory_scene=task["env_name"],robot_base_pos=gp["pos"],robot_base_ori=[0,0,gp["yaw"]],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
wrapped=make_eval_env(ns,config=backend._physics_config,ckpt_dict=backend._physics_ckpt_dict,render=False)
wrapped.reset()
raw=base_robosuite_env(wrapped)
raw.sim.forward()
robot=raw.robots[0]

# args for scripted grasp (from demo policy_info)
args=argparse.Namespace(
    site_below_offset=0.035, show_object_sites=False, object_site_size=0.04,
    camera="robot0_robotview", render_sleep=0.0,
    up_steps=30, xy_steps=60, down_steps=40,
    safe_z=0.1, site_above_clearance=0.05,
    arrival_tolerance=0.025, gripper_end_arrival_tolerance=0.03,
    settle_steps=40, grasp_steps=25, max_action=0.65,
    initial_view_steps=15,
)
# dummy obs_buffer (not needed for grasp, just pass empty dict-like)
class DummyBuf:
    def __init__(self): self.data={}
obs_buffer=DummyBuf()

# get targets
below_targets, site_names = col.get_target_positions(raw, obj_name, args.site_below_offset)
print("below_targets:", {k: v.tolist() for k,v in below_targets.items()})
starts = {arm: col.get_eef_pos(raw, robot, arm) for arm in col.ARMS}
print("starts:", {k: v.tolist() for k,v in starts.items()})
safe_z = max(args.safe_z, max(starts[a][2] for a in col.ARMS), max(below_targets[a][2]+args.site_above_clearance for a in col.ARMS))
safe_targets = {a: np.array([starts[a][0], starts[a][1], safe_z]) for a in col.ARMS}
xy_targets = {a: np.array([below_targets[a][0], below_targets[a][1], safe_z]) for a in col.ARMS}
print("safe_z:", safe_z)

# 1. up
ok, reason = col.move_along_linear_segment(wrapped, raw, robot, obj_name, safe_targets, args.up_steps, -1.0, False, args, obs_buffer, reject_object_contact=True, label="up")
print("up:", ok, reason)
# 2. xy
if ok:
    ok, reason = col.move_along_linear_segment(wrapped, raw, robot, obj_name, xy_targets, args.xy_steps, -1.0, False, args, obs_buffer, reject_object_contact=True, label="xy")
    print("xy:", ok, reason)
# 3. down
if ok:
    ok, reason = col.move_vertically_below_sites(wrapped, raw, robot, below_targets, {a: below_targets[a]+np.array([0,0,args.site_below_offset]) for a in col.ARMS}, args.down_steps, -1.0, False, args, obs_buffer, label="down")
    print("down:", ok, reason)
# 4. settle
if ok:
    ok, reason = col.settle_gripper_end_centers_at_targets(wrapped, raw, robot, below_targets, -1.0, False, args, obs_buffer, label="settle")
    print("settle:", ok, reason)
# 5. grasp close
if ok:
    for _ in range(args.grasp_steps):
        action = col.build_action(raw, robot, {}, gripper_value=1.0)
        wrapped.step(action)
    print("grasp steps done")
    _, grasps = print_grasp_debug_info(raw, robot, obj_name, below_targets, label="after grasp")
    print("grasp_status:", grasps)
    success = all(grasps.values())
    print("SCRIPTED GRASP SUCCESS:", success)

# check eef pos
for arm in col.ARMS:
    print(f"eef {arm}:", col.get_eef_pos(raw, robot, arm).tolist())
backend.close()
print("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_scripted_grasp_test.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_scripted_grasp_test.py'],stdout=open('/mnt/workspace/_scripted_grasp_test.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

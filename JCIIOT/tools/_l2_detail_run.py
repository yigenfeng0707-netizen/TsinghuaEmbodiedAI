import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, json, numpy as np, argparse, traceback as _tb
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
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env

cfg=json.load(open(P(APP)/"knowledge"/"task_config.json"))
task=next(t for t in cfg["tasks"] if t["level"]=="L2")
gp=cfg["grasp_poses"][task["source"]]
obj_name=task["object"]
log(f"L2 base={gp['pos']} obj={obj_name}")

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
below_targets,_=col.get_target_positions(raw, obj_name, 0.035)
starts={arm: col.get_eef_pos(raw, robot, arm) for arm in col.ARMS}
safe_z=max(0.10, max(starts[a][2] for a in col.ARMS), max(below_targets[a][2]+0.05 for a in col.ARMS))
safe_targets={a: np.array([starts[a][0], starts[a][1], safe_z]) for a in col.ARMS}
xy_targets={a: np.array([below_targets[a][0], below_targets[a][1], safe_z]) for a in col.ARMS}
log("starts:", {k:v.tolist() for k,v in starts.items()})
log("safe_z:", safe_z, "safe_targets:", {k:v.tolist() for k,v in safe_targets.items()})
log("xy_targets:", {k:v.tolist() for k,v in xy_targets.items()})

args=argparse.Namespace(site_below_offset=0.035,show_object_sites=False,object_site_size=0.04,camera="robot0_robotview",render_sleep=0.0,up_steps=40,xy_steps=60,down_steps=40,safe_z=0.10,site_above_clearance=0.05,arrival_tolerance=0.04,gripper_end_arrival_tolerance=0.04,settle_steps=60,grasp_steps=25,max_action=0.65,initial_view_steps=15)
class DB: pass
ok,reason=col.move_along_linear_segment(wrapped, raw, robot, obj_name, safe_targets, args.up_steps, -1.0, False, args, DB(), reject_object_contact=True, label="up")
log("up:", ok, reason[:100] if reason else "")
for arm in col.ARMS:
    log(f"  eef {arm} after up: {col.get_eef_pos(raw, robot, arm).tolist()} target {safe_targets[arm].tolist()} dist {np.linalg.norm(col.get_eef_pos(raw,robot,arm)-safe_targets[arm]):.3f}")
if ok:
    ok,reason=col.move_along_linear_segment(wrapped, raw, robot, obj_name, xy_targets, args.xy_steps, -1.0, False, args, DB(), reject_object_contact=True, label="xy")
    log("xy:", ok, reason[:100] if reason else "")
    for arm in col.ARMS:
        log(f"  eef {arm} after xy: {col.get_eef_pos(raw, robot, arm).tolist()} target {xy_targets[arm].tolist()} dist {np.linalg.norm(col.get_eef_pos(raw,robot,arm)-xy_targets[arm]):.3f}")
backend.close()
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_l2_detail.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_l2_detail.py'],stdout=open('/mnt/workspace/_l2_detail.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

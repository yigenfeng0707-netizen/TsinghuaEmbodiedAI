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
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env
import robot_agent.environments.robosuite_backend as RB
from robosuite.utils.transform_utils import mat2euler

def get_arm_info(raw, robot, arm):
    eef_site = robot.eef_site_id[arm]
    epos = raw.sim.data.site_xpos[eef_site]
    emat = raw.sim.data.get_site_xmat(raw.sim.model.site_id2name(eef_site)).flatten()
    euler = mat2euler(emat.reshape(3,3))
    # arm joints
    arm_joints = getattr(robot, "robot_arm_joints", [])
    arm_joints = [j for j in arm_joints if arm in j]
    qpos_vals = []
    for jn in arm_joints[:7]:
        try:
            qpos_vals.append(round(float(raw.sim.data.get_joint_qpos(jn)),3))
        except: pass
    return epos.tolist(), round(euler[2],3), qpos_vals

# L1 container
cfg=json.load(open(P(APP)/"knowledge"/"task_config.json"))
for lvl in ["L1","L2"]:
    task=next(t for t in cfg["tasks"] if t["level"]==lvl)
    gp=cfg["grasp_poses_by_level"][lvl]
    obj_name=task["object"]
    log(f"=== {lvl}: base={gp['pos']} obj={obj_name} ===")
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
    # initial arm info (before grasp)
    for arm in col.ARMS:
        pos, ez, qpos = get_arm_info(raw, robot, arm)
        log(f"  INIT {arm}: eef={pos} euler_z={ez} arm_qpos={qpos}")
    # run grasp
    RB._scripted_grasp_in_wrapped_env(wrapped, raw, obj_name, headless=True, render_callback=None)
    for arm in col.ARMS:
        pos, ez, qpos = get_arm_info(raw, robot, arm)
        log(f"  AFTER {arm}: eef={pos} euler_z={ez} arm_qpos={qpos}")
    backend.close()
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_arm_compare.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_arm_compare.py'],stdout=open('/mnt/workspace/_arm_compare.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

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
for lvl in ["L2","L3","L5"]:
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
    below_targets,_=col.get_target_positions(raw, obj_name, 0.035)
    starts={arm: col.get_eef_pos(raw, robot, arm) for arm in col.ARMS}
    safe_z=max(0.10, max(starts[a][2] for a in col.ARMS), max(below_targets[a][2]+0.15 for a in col.ARMS))
    safe_targets={a: np.array([starts[a][0], starts[a][1], safe_z]) for a in col.ARMS}
    xy_targets={a: np.array([below_targets[a][0], below_targets[a][1], safe_z]) for a in col.ARMS}
    log(f"  starts: R={starts['right'].tolist()} L={starts['left'].tolist()}")
    log(f"  below_targets: R={below_targets['right'].tolist()} L={below_targets['left'].tolist()}")
    log(f"  safe_z={safe_z:.3f}")
    log(f"  xy_targets: R={xy_targets['right'].tolist()} L={xy_targets['left'].tolist()}")
    # xy distance each arm
    for arm in col.ARMS:
        d=np.linalg.norm(starts[arm][:2]-xy_targets[arm][:2])
        log(f"  {arm} xy distance to move: {d:.3f}")
    # object bbox (collision geoms)
    geoms=col.object_collision_geoms(raw, obj_name)
    log(f"  obj collision geoms: {geims if False else geoms[:3]}")
    # object site positions (top)
    for sn in [f"{obj_name}_center_site", f"{obj_name}_default_site"]:
        try:
            sid=raw.sim.model.site_name2id(sn)
            log(f"  site {sn}: {raw.sim.data.site_xpos[sid].tolist()}")
        except: pass
    backend.close()
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_tote_diag.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_tote_diag.py'],stdout=open('/mnt/workspace/_tote_diag.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

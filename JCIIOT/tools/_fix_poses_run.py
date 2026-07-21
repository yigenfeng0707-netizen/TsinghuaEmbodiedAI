import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, json, numpy as np, argparse, math
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"
os.environ["GATE_OLLAMA"]="false"; os.environ["GATE_STEP_TIMEOUT"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
def log(*a): print(*a, flush=True)

from robot_agent.environments import RobosuiteBackend
from robosuite.environments.factory_sorting.load_factory_sorting_evalization import make_eval_env, base_robosuite_env, object_grasp_site_name

# L1 reference: base=[8.0,4.6] obj=[7.349,4.619] yaw=-3.14
# base is at obj + [dx, dy] where dx=cos(yaw+pi)*0.65, dy=sin(yaw+pi)*0.65
# yaw=-3.14 => facing -x => base at obj + [+0.65, 0]
L1_base=np.array([8.0,4.6]); L1_obj=np.array([7.349,4.619])
L1_offset = L1_base - L1_obj
log(f"L1 offset base-obj: {L1_offset.tolist()} (dist={np.linalg.norm(L1_offset):.3f})")

cfg=json.load(open(P(APP)/"knowledge"/"task_config.json"))
new_poses={}
for lvl in ["L2","L3","L4","L5"]:
    task=next(t for t in cfg["tasks"] if t["level"]==lvl)
    gp=cfg["grasp_poses"][task["source"]]
    obj_name=task["object"]
    yaw=gp["yaw"]
    backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
    objs=tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"],{})
    backend.set_physics_grasp_config(device="cpu",object_map=objs)
    backend.reset()
    # use config pose first to load env, then read obj pos
    ns=argparse.Namespace(factory_scene=task["env_name"],robot_base_pos=gp["pos"],robot_base_ori=[0,0,yaw],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
    wrapped=make_eval_env(ns,config=backend._physics_config,ckpt_dict=backend._physics_ckpt_dict,render=False)
    wrapped.reset()
    raw=base_robosuite_env(wrapped)
    raw.sim.forward()
    rsite=raw.sim.data.site_xpos[raw.sim.model.site_name2id(object_grasp_site_name(obj_name,"right"))]
    lsite=raw.sim.data.site_xpos[raw.sim.model.site_name2id(object_grasp_site_name(obj_name,"left"))]
    grasp_mid=np.array([(rsite[0]+lsite[0])/2, (rsite[1]+lsite[1])/2])
    # correct base = grasp_mid + L1_offset (same relative offset)
    new_base = grasp_mid + L1_offset
    log(f"{lvl}: obj_grasp_mid={grasp_mid.tolist()} yaw={yaw} -> new_base={new_base.tolist()}")
    new_poses[task["source"]] = {"pos": [round(new_base[0],3), round(new_base[1],3), 0.0], "yaw": yaw}
    backend.close()

# update task_config.json grasp_poses
for src, pose in new_poses.items():
    cfg["grasp_poses"][src] = pose
    # also set line_* alias
    if src.startswith("input_"):
        line_name = "line_" + src.split("_",1)[1]
        cfg["grasp_poses"][line_name] = pose
json.dump(cfg, open(P(APP)/"knowledge"/"task_config.json","w"), indent=2, ensure_ascii=False)
log("task_config.json updated with corrected grasp_poses")
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_fix_poses.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_fix_poses.py'],stdout=open('/mnt/workspace/_fix_poses.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

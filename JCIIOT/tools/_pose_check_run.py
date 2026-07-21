import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, json, numpy as np, argparse
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

cfg=json.load(open(P(APP)/"knowledge"/"task_config.json"))
for lvl in ["L1","L2","L3","L4","L5"]:
    task=next(t for t in cfg["tasks"] if t["level"]==lvl)
    gp=cfg["grasp_poses"][task["source"]]
    obj_name=task["object"]
    try:
        backend=RobosuiteBackend(env_name=task["env_name"],camera="birdview",headless=True,drive_mode="direct")
        objs=tsr.SCENE_INPUT_OBJECT_MAP.get(task["env_name"],{})
        backend.set_physics_grasp_config(device="cpu",object_map=objs)
        backend.reset()
        ns=argparse.Namespace(factory_scene=task["env_name"],robot_base_pos=gp["pos"],robot_base_ori=[0,0,gp["yaw"]],renderer="mjviewer",camera="robot0_robotview",camera_height=128,camera_width=128,controller=None,gripper_types="Robotiq140Gripper",seed=None)
        wrapped=make_eval_env(ns,config=backend._physics_config,ckpt_dict=backend._physics_ckpt_dict,render=False)
        wrapped.reset()
        raw=base_robosuite_env(wrapped)
        raw.sim.forward()
        # object center site
        try:
            csid=raw.sim.model.site_name2id(f"{obj_name}_center_site")
            cpos=raw.sim.data.site_xpos[csid].tolist()
        except:
            cpos=None
        # grasp sites
        rsite=raw.sim.data.site_xpos[raw.sim.model.site_name2id(object_grasp_site_name(obj_name,"right"))].tolist()
        lsite=raw.sim.data.site_xpos[raw.sim.model.site_name2id(object_grasp_site_name(obj_name,"left"))].tolist()
        grasp_center=[(rsite[0]+lsite[0])/2, (rsite[1]+lsite[1])/2]
        # base pose from config
        log(f"{lvl}: base={gp['pos'][:2]} obj_center={cpos[:2] if cpos else grasp_center} grasp_mid={grasp_center} dist_base_to_obj={np.linalg.norm(np.array(gp['pos'][:2])-grasp_center):.3f}")
        backend.close()
    except Exception as e:
        log(f"{lvl} FAIL: {repr(e)[:120]}")
log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_pose_check.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_pose_check.py'],stdout=open('/mnt/workspace/_pose_check.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))

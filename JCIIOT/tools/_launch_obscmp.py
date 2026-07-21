import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

CKPT = "/mnt/workspace/JCIIOT_repo/JCIIOT/bc_trained_models/l1_run_v2/l1_bc_v7/20260718144623/models/model_epoch_50.pth"
HDF5 = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5"
EVFILE = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py"

INNER = '''import os, sys, h5py, numpy as np, importlib.util, argparse, pathlib
os.environ["MUJOCO_GL"]="osmesa"
sys.path.insert(0, "/mnt/workspace/JCIIOT_repo/JCIIOT")
spec = importlib.util.spec_from_file_location("ffeval", "__EVFILE__")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
args = argparse.Namespace(
    checkpoint=pathlib.Path("__CKPT__"), factory_scene="factory_sorting_1_3fo3erfhisem",
    num_rollouts=1, eval_steps=None, device="cpu", debug_policy=False, debug_every=1,
    verbose=False, object_name="line_5_container_h01_near", site_below_offset=0.035,
    post_hold_steps=10, initial_view_steps=0, render_sleep=0.0, camera_height=128,
    camera_width=128, show_object_sites=False, object_site_size=0.02,
    robot_base_pos=[8.000001,4.600000,0.0], robot_base_ori=[0.0,0.0,3.139422],
    renderer="mjviewer", camera="robot0_robotview", controller=None,
    gripper_types="Robotiq140Gripper", seed=None, no_render=True, save_grasp_init_state=None)
policy, config, ckpt_dict = mod.load_policy_and_config(args)
env = mod.make_eval_env(args, config=config, ckpt_dict=ckpt_dict, render=False)
f = h5py.File("__HDF5__","r")
demo_obs = {k: f["data/demo_1/obs/"+k][0] for k in f["data/demo_1/obs"].keys()}
f.close()
env.reset(); st = env.get_state(); obs = env.reset_to(st)
KEYS=["robot0_left_eef_pos","robot0_left_eef_quat","robot0_left_gripper_qpos","robot0_right_eef_pos","robot0_right_eef_quat","robot0_right_gripper_qpos"]
for k in KEYS:
    d = np.asarray(demo_obs[k], dtype=float).flatten()
    e = np.asarray(obs[k], dtype=float).flatten()
    if d.shape==e.shape:
        print(k, "maxabsdiff", round(float(np.max(np.abs(d-e))),5), "demo", np.round(d[:4],3), "eval", np.round(e[:4],3))
    else:
        print(k, "SHAPE MISMATCH demo", d.shape, "eval", e.shape)
img_d = demo_obs.get("robot0_robotview_image")
img_e = obs.get("robot0_robotview_image")
print("img demo shape", None if img_d is None else np.asarray(img_d).shape, "eval shape", None if img_e is None else np.asarray(img_e).shape)
'''
c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_obscmp.py", json={"type":"file","format":"text","content":INNER.replace("__CKPT__",CKPT).replace("__HDF5__",HDF5).replace("__EVFILE__",EVFILE)}, timeout=30)
print(c.run_python("import subprocess,os\nenv={**os.environ,'MUJOCO_GL':'osmesa','OMP_NUM_THREADS':'8','OPENBLAS_NUM_THREADS':'8','MKL_NUM_THREADS':'8','NUMEXPR_NUM_THREADS':'8'}\nr=subprocess.Popen(['nohup','python','/mnt/workspace/_obscmp.py'],stdout=open('/mnt/workspace/_obscmp.log','w'),stderr=subprocess.STDOUT,start_new_session=True,env=env)\nprint('launched',r.pid)", timeout=60))

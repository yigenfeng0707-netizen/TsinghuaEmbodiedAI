import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

NEW_HDF5 = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181720_noholdhead/202607181603/nohold_demo_202607181603.hdf5"
EVFILE = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py"
CKPT = "/mnt/workspace/JCIIOT_repo/JCIIOT/bc_trained_models/l1_run_v2/l1_bc_lordim_v1/20260718153644/models/model_epoch_50.pth"

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
# load checkpoint just to initialize ObsUtils, then build env with image obs
policy, config, ckpt_dict = mod.load_policy_and_config(args)
import robomimic.utils.obs_utils as ObsUtils
ObsUtils.initialize_obs_utils_with_config(config)
from robomimic.envs.env_robosuite import EnvRobosuite
env_name = mod.factory_scene_env_name(args)
env = EnvRobosuite(env_name=env_name, render=False, render_offscreen=True,
                   use_image_obs=True, use_depth_obs=False,
                   **mod.make_factory_sorting_env_kwargs(args))
f = h5py.File("__NEW__","r")
new_img = np.asarray(f["data/demo_1/obs/robot0_robotview_image"][0], dtype=float)
f.close()
env.reset(); st = env.get_state(); obs = env.reset_to(st)
eval_img = np.asarray(obs["robot0_robotview_image"], dtype=float)
print("new_demo_img shape", new_img.shape, "eval_img shape", eval_img.shape)
print("img maxabsdiff new_vs_eval:", float(np.max(np.abs(new_img-eval_img))))
# also compare against the OLD demo image (head-hold) for reference
OLD="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181306/l1_20_202607181306.hdf5"
fo=h5py.File(OLD,"r"); old_img=np.asarray(fo["data/demo_1/obs/robot0_robotview_image"][0],dtype=float); fo.close()
print("img maxabsdiff old_vs_eval:", float(np.max(np.abs(old_img-eval_img))))
print("img maxabsdiff old_vs_new:", float(np.max(np.abs(old_img-new_img))))
'''
c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_imgcmp2.py", json={"type":"file","format":"text","content":INNER.replace("__NEW__",NEW_HDF5).replace("__EVFILE__",EVFILE).replace("__CKPT__",CKPT)}, timeout=30)
print(c.run_python("import subprocess,os\nenv={**os.environ,'MUJOCO_GL':'osmesa','OMP_NUM_THREADS':'8','OPENBLAS_NUM_THREADS':'8','MKL_NUM_THREADS':'8','NUMEXPR_NUM_THREADS':'8'}\nr=subprocess.Popen(['nohup','python','/mnt/workspace/_imgcmp2.py'],stdout=open('/mnt/workspace/_imgcmp2.log','w'),stderr=subprocess.STDOUT,start_new_session=True,env=env)\nprint('launched',r.pid)", timeout=60))

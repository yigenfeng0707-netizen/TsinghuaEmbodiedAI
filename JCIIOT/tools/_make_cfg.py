import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import json, glob, os
base = "/mnt/workspace/JCIIOT_repo/JCIIOT"
tmpl = json.load(open(base + "/robomimic/exps/templates/bc.json"))
hits = glob.glob(base + "/robosuite/robosuite/models/assets/demonstrations_private/*/l1_20_*.hdf5")
ds = hits[0]
print("dataset:", ds)

# override train settings
tmpl["train"]["data"] = ds
tmpl["train"]["dataset_keys"] = ["actions"]
tmpl["train"]["num_data_workers"] = 0
tmpl["train"]["hdf5_cache_mode"] = "all"
tmpl["train"]["output_dir"] = base + "/bc_trained_models"
tmpl["train"]["num_epochs"] = 50
tmpl["train"]["seed"] = 42

# observation modalities match the dual-arm Tiago demo
tmpl["observation"]["modalities"]["obs"]["low_dim"] = [
    "robot0_left_eef_pos", "robot0_left_eef_quat", "robot0_left_gripper_qpos",
    "robot0_right_eef_pos", "robot0_right_eef_quat", "robot0_right_gripper_qpos",
]
tmpl["observation"]["modalities"]["obs"]["rgb"] = ["robot0_robotview_image"]
tmpl["observation"]["modalities"]["goal"]["low_dim"] = []
tmpl["observation"]["modalities"]["goal"]["rgb"] = []

# algo
tmpl["algo"]["algo_name"] = "bc"
tmpl["algo"]["optim_params"]["policy"]["learning_rate"]["initial"] = 1e-3

# experiment
tmpl["experiment"]["env"] = None
tmpl["experiment"]["validate"] = False
tmpl["experiment"]["logging"]["terminal_output_to_txt"] = True

out = base + "/bc_l1_config.json"
json.dump(tmpl, open(out, "w"), indent=2)
print("wrote config:", out)
print("train.data:", tmpl["train"]["data"])
print("dataset_keys:", tmpl["train"]["dataset_keys"])
print("low_dim:", tmpl["observation"]["modalities"]["obs"]["low_dim"])
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_make_cfg.py", json=payload, timeout=30)
code = (
    "import subprocess, os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa'}\n"
    "r=subprocess.run(['python','/mnt/workspace/_make_cfg.py'],capture_output=True,text=True,timeout=120,env=env)\n"
    "print('RC',r.returncode); print(r.stdout[-600:]); print('ERR',r.stderr[-400:])\n"
)
print(c.run_python(code, timeout=150))

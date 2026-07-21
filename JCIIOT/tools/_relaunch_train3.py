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
tmpl["train"]["data"] = [{"path": ds, "lang": None}]
tmpl["train"]["dataset_keys"] = ["actions"]
tmpl["train"]["num_data_workers"] = 0
tmpl["train"]["hdf5_cache_mode"] = "all"
tmpl["train"]["output_dir"] = base + "/bc_trained_models/l1_run_v2"
tmpl["train"]["num_epochs"] = 300
tmpl["train"]["seed"] = 42
tmpl["observation"]["modalities"]["obs"]["low_dim"] = [
    "robot0_left_eef_pos", "robot0_left_eef_quat", "robot0_left_gripper_qpos",
    "robot0_right_eef_pos", "robot0_right_eef_quat", "robot0_right_gripper_qpos",
]
tmpl["observation"]["modalities"]["obs"]["rgb"] = []
tmpl["observation"]["modalities"]["goal"]["low_dim"] = []
tmpl["observation"]["modalities"]["goal"]["rgb"] = []
tmpl["algo_name"] = "bc"
tmpl["algo"]["optim_params"]["policy"]["learning_rate"]["initial"] = 3e-4
tmpl["experiment"]["env"] = None
tmpl["experiment"]["validate"] = False
tmpl["experiment"]["name"] = "l1_bc_lordim_v2"
if "rollout" in tmpl["experiment"]:
    tmpl["experiment"]["rollout"]["enabled"] = False
if "overwrite" in tmpl["experiment"]["save"]:
    tmpl["experiment"]["save"]["overwrite"] = True
tmpl["experiment"]["logging"]["terminal_output_to_txt"] = True
tmpl["experiment"]["logging"]["log_tb"] = False
tmpl["experiment"]["logging"]["log_wandb"] = False
out = base + "/bc_l1_config.json"
json.dump(tmpl, open(out, "w"), indent=2)
print("wrote", out)
'''

TRAIN = '''import os, subprocess
os.environ["MUJOCO_GL"]="osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
os.environ["HF_HUB_OFFLINE"]="1"
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"]:
    os.environ[v]="8"
cmd=["python","/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/scripts/train.py","--config","/mnt/workspace/JCIIOT_repo/JCIIOT/bc_l1_config.json"]
with open("/mnt/workspace/_train.log","w") as log:
    r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=21600,env=os.environ.copy())
    log.write("\\nTRAIN_RC=%d\\n"%r.returncode)
print("train rc",r.returncode)
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_make_cfg.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
c.s.put(d.BASE + "/api/contents/_train.py", json={"type":"file","format":"text","content":TRAIN}, timeout=30)

reg = "import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_make_cfg.py'],capture_output=True,text=True,timeout=120,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout[-300:], r.stderr[-300:])"
print("REGEN:", c.run_python(reg, timeout=150))

launch = (
    "import subprocess,os\n"
    "subprocess.run('pkill -9 -f robomimic/scripts/train.py', shell=True)\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa','OMP_NUM_THREADS':'8','OPENBLAS_NUM_THREADS':'8','MKL_NUM_THREADS':'8','NUMEXPR_NUM_THREADS':'8'}\n"
    "r=subprocess.Popen(['nohup','python','/mnt/workspace/_train.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env=env)\n"
    "print('relaunched pid', r.pid)\n"
)
print("LAUNCH:", c.run_python(launch, timeout=60))

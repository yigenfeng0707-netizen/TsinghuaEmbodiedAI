import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

CKPT = "/mnt/workspace/JCIIOT_repo/JCIIOT/bc_trained_models/l1_run_v2/l1_bc_v7/20260718144623/models/model_epoch_50.pth"
SCENE = "factory_sorting_1_3fo3erfhisem"

INNER = '''import os, subprocess
os.environ["MUJOCO_GL"]="osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
os.environ.pop("HF_HUB_OFFLINE", None)
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"]:
    os.environ[v]="8"
script="/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py"
ckpt="%s"
scene="%s"
cmd=["python", script, "--checkpoint", ckpt, "--factory-scene", scene, "--num-rollouts", "1", "--no-render", "--device", "cpu"]
with open("/mnt/workspace/_eval.log","w") as log:
    r=subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=1800, env=os.environ.copy())
    log.write("\\nEVAL_RC=%d\\n" % r.returncode)
print("eval rc", r.returncode)
''' % (CKPT, SCENE)

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_eval.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
launch = (
    "import subprocess,os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa','OMP_NUM_THREADS':'8','OPENBLAS_NUM_THREADS':'8','MKL_NUM_THREADS':'8','NUMEXPR_NUM_THREADS':'8'}\n"
    "r=subprocess.Popen(['nohup','python','/mnt/workspace/_eval.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env=env)\n"
    "print('launched eval pid',r.pid)\n"
)
print(c.run_python(launch, timeout=60))

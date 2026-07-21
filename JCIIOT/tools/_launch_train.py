import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import os, subprocess
os.environ["MUJOCO_GL"] = "osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"]:
    os.environ[v] = "8"
script = "/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/scripts/train.py"
cfg = "/mnt/workspace/JCIIOT_repo/JCIIOT/bc_l1_config.json"
cmd = ["python", script, "--config", cfg]
with open("/mnt/workspace/_train.log", "w") as log:
    r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=21600, env=os.environ.copy())
    log.write("\\nTRAIN_RC=%d\\n" % r.returncode)
print("train rc", r.returncode)
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_train.py", json=payload, timeout=30)
code = (
    "import subprocess, os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa','OMP_NUM_THREADS':'8','OPENBLAS_NUM_THREADS':'8','MKL_NUM_THREADS':'8','NUMEXPR_NUM_THREADS':'8'}\n"
    "r=subprocess.Popen(['nohup','python','/mnt/workspace/_train.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env=env)\n"
    "print('launched train pid',r.pid)\n"
)
print(c.run_python(code, timeout=60))

import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

c = d.Dswhub()
# kill stale train
kill = "import subprocess\nsubprocess.run('pkill -9 -f robomimic/scripts/train.py', shell=True)\nprint('killed')\n"
c.s.put(d.BASE + "/api/contents/_k.py", json={"type":"file","format":"text","content":kill}, timeout=30)
print(c.run_python("import subprocess,os,time\nsubprocess.run(['python','/mnt/workspace/_k.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); time.sleep(2); print('ok')", timeout=90))

# regenerate config
reg = "import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_make_cfg.py'],capture_output=True,text=True,timeout=120,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout[-400:], r.stderr[-300:])"
print(c.run_python(reg, timeout=150))

# relaunch train
INNER = '''import os, subprocess
os.environ["MUJOCO_GL"]="osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"]:
    os.environ[v]="8"
cmd=["python","/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/scripts/train.py","--config","/mnt/workspace/JCIIOT_repo/JCIIOT/bc_l1_config.json"]
with open("/mnt/workspace/_train.log","w") as log:
    r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=21600,env=os.environ.copy())
    log.write("\\nTRAIN_RC=%d\\n"%r.returncode)
print("train rc",r.returncode)
'''
c.s.put(d.BASE + "/api/contents/_train.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nenv={**os.environ,'MUJOCO_GL':'osmesa','OMP_NUM_THREADS':'8','OPENBLAS_NUM_THREADS':'8','MKL_NUM_THREADS':'8','NUMEXPR_NUM_THREADS':'8'}\nr=subprocess.Popen(['nohup','python','/mnt/workspace/_train.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env=env)\nprint('relaunched train pid',r.pid)", timeout=60))

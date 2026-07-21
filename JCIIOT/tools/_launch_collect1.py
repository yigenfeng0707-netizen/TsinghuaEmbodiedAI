import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

COLL = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
OUT = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/models/assets/demonstrations_private/202607181720_noholdhead"

INNER = '''import os, subprocess, sys
os.environ["MUJOCO_GL"]="osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"]:
    os.environ[v]="8"
cmd=["python","__COLL__","--num-rollouts","1","--directory","__OUT__","--output-name","nohold_demo","--no-render"]
with open("/mnt/workspace/_collect1.log","w") as log:
    r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=1800,env=os.environ.copy())
    log.write("\\nCOLLECT_RC=%d\\n"%r.returncode)
print("collect rc",r.returncode)
'''.replace("__COLL__", COLL).replace("__OUT__", OUT)

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_collect1.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
launch = (
    "import subprocess,os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa','OMP_NUM_THREADS':'8','OPENBLAS_NUM_THREADS':'8','MKL_NUM_THREADS':'8','NUMEXPR_NUM_THREADS':'8'}\n"
    "r=subprocess.Popen(['nohup','python','/mnt/workspace/_collect1.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env=env)\n"
    "print('launched collect pid',r.pid)\n"
)
print(c.run_python(launch, timeout=60))

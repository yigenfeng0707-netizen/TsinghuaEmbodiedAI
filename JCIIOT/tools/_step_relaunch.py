import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

launch_py = (
    "import os, subprocess\n"
    "os.environ['MUJOCO_GL']='osmesa'\n"
    "os.environ.pop('PYOPENGL_PLATFORM', None)\n"
    "for v in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:\n"
    "    os.environ[v]='8'\n"
    "script='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "cmd=['python',script,'--num-rollouts','50','--no-render','--output-name','l1_50']\n"
    "with open('/mnt/workspace/_collect50b.log','w') as log:\n"
    "    r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=21600,env=os.environ.copy())\n"
    "    log.write('\\nCOLLECT_RC=%d\\n'%r.returncode)\n"
    "print('collect rc',r.returncode)\n"
)
c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_collect50b.py", json={"type":"file","format":"text","content":launch_py}, timeout=30)
print(c.run_python(
    "import subprocess,os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa','OMP_NUM_THREADS':'8','OPENBLAS_NUM_THREADS':'8','MKL_NUM_THREADS':'8','NUMEXPR_NUM_THREADS':'8'}\n"
    "r=subprocess.Popen(['nohup','python','/mnt/workspace/_collect50b.py'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env=env)\n"
    "print('relaunched pid',r.pid)", timeout=60))

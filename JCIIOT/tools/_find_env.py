import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,os,glob\n"
    "# find conda\n"
    "r=subprocess.run('which conda',shell=True,capture_output=True,text=True); print('conda:',r.stdout.strip() or 'none')\n"
    "# list conda envs\n"
    "r=subprocess.run('conda env list',shell=True,capture_output=True,text=True); print('ENVS:\\n'+r.stdout[:800])\n"
    "# search for mujoco in common conda paths\n"
    "for base in ['/opt/conda','/root/anaconda3','/usr/local','/mnt/workspace/miniconda3']:\n"
    "    p=os.path.join(base,'bin','python')\n"
    "    if os.path.exists(p):\n"
    "        t=subprocess.run([p,'-c','import mujoco; print(\"mujoco\",mujoco.__version__)'],capture_output=True,text=True)\n"
    "        print(base,'->', 'OK '+t.stdout.strip() if t.returncode==0 else 'no mujoco')\n"
    "# also check /root and /opt conda envs dirs\n"
    "for d in glob.glob('/opt/conda/envs/*/bin/python')+glob.glob('/root/anaconda3/envs/*/bin/python')+glob.glob('/root/.conda/envs/*/bin/python'):\n"
    "    t=subprocess.run([d,'-c','import mujoco;print(1)'],capture_output=True,text=True)\n"
    "    print(d,'mujoco' if t.returncode==0 else 'no')\n"
)
print(d.Dswhub().run_python(code, timeout=90))

import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess,os,glob,shutil\n"
    "print('PATH:', os.environ.get('PATH'))\n"
    "for tool in ['micromamba','mamba','conda','python3.12','python3.11']:\n"
    "    print(tool, shutil.which(tool))\n"
    "# search common install roots\n"
    "for root in ['/root','/opt','/mnt/workspace','/usr/local','/home']:\n"
    "    for pat in ['*/bin/micromamba','*/bin/mamba','*/bin/conda','*/etc/profile.d/conda.sh','*/micromamba','*/miniconda3']:\n"
    "        for f in glob.glob(os.path.join(root,pat))[:3]:\n"
    "            print('FOUND', f)\n"
    "# find any python with mujoco by scanning /mnt/workspace and /root for site-packages\n"
    "for sp in glob.glob('/root/*/lib/python*/site-packages/mujoco')+glob.glob('/mnt/workspace/*/lib/python*/site-packages/mujoco')+glob.glob('/opt/*/lib/python*/site-packages/mujoco'):\n"
    "    print('MUJOCO SP:', sp)\n"
    "print('--- history ---')\n"
    "r=subprocess.run('cat ~/.bash_history 2>/dev/null | tail -20',shell=True,capture_output=True,text=True); print(r.stdout)\n"
)
print(d.Dswhub().run_python(code, timeout=90))

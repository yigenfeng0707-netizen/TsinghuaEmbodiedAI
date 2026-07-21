import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py'\n"
    "src=open(p).read()\n"
    "i=src.find('def run_factory_sorting_grasp(')\n"
    "print(src[i+1500:i+3200])\n"
)
print(d.Dswhub().run_python(code, timeout=60))

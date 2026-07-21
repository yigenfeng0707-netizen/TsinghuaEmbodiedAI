import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "src=open(p).read()\n"
    "i=src.find('def build_action')\n"
    "print(src[i:i+1400])\n"
)
print(d.Dswhub().run_python(code, timeout=60))

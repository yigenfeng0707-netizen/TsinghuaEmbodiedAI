import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "base='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py'\n"
    "t=open(base).read()\n"
    "i=t.find('def load_factory_sorting_policy')\n"
    "print(t[i:i+2600])\n"
)
print(d.Dswhub().run_python(code, timeout=60))

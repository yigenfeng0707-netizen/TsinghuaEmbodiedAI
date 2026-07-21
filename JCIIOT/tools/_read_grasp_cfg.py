import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "base='/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/environments/robosuite_backend.py'\n"
    "t=open(base).read()\n"
    "s=t.find('def set_physics_grasp_config')\n"
    "print(t[s:s+3500])\n"
)
print(d.Dswhub().run_python(code, timeout=60))

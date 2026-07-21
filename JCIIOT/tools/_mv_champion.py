import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import shutil, os\n"
    "src='/mnt/workspace/champion_transport.py'\n"
    "dst='/mnt/workspace/JCIIOT_repo/JCIIOT/src/robot_agent/workflows/champion_transport.py'\n"
    "os.makedirs(os.path.dirname(dst), exist_ok=True)\n"
    "shutil.move(src, dst)\n"
    "print('moved ->', dst, os.path.getsize(dst))\n"
)
print(d.Dswhub().run_python(code, timeout=60))

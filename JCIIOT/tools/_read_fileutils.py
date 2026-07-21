import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/utils/file_utils.py'\n"
    "lines=open(p).read().splitlines()\n"
    "for i in range(95,140):\n"
    "    if i-1 < len(lines): print(i, lines[i-1][:160])\n"
)
print(d.Dswhub().run_python(code, timeout=60))

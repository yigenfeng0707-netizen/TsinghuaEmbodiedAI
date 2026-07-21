import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/utils/lang_utils.py'\n"
    "print(open(p).read()[:2500])\n"
)
print(d.Dswhub().run_python(code, timeout=60))

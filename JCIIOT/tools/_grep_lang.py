import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robomimic/utils/env_utils.py'\n"
    "src=open(p).read()\n"
    "import re\n"
    "for m in re.finditer(r'lang', src):\n"
    "    s=max(0,m.start()-120); print(repr(src[s:m.start()+80])); print('---')\n"
)
print(d.Dswhub().run_python(code, timeout=60))

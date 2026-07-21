import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os\n"
    "txt=open('/mnt/workspace/_train.log').read().splitlines()\n"
    "for l in txt[-40:]:\n"
    "    if 'L2_Loss' in l or 'Loss' in l: print(l[:120])\n"
)
print(d.Dswhub().run_python(code, timeout=60))

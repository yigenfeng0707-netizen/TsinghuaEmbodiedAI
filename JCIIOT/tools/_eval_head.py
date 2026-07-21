import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os\n"
    "txt=open('/mnt/workspace/_eval.log').read().splitlines()\n"
    "for i,l in enumerate(txt[:40]): print(i, l[:170])\n"
)
print(d.Dswhub().run_python(code, timeout=60))

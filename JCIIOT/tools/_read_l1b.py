import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "print(repr(open('/mnt/workspace/_run_l1b.log').read()[-3000:]))"
)
print(d.Dswhub().run_python(code, timeout=60))

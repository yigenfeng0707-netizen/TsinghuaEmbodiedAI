import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "print(open('/mnt/workspace/_run_l1.out').read())"
)
print(d.Dswhub().run_python(code, timeout=90))

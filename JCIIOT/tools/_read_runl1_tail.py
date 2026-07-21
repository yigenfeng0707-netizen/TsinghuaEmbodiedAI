import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "lines=open('/mnt/workspace/_run_l1.out').read().splitlines()\n"
    "print('TOTAL LINES', len(lines))\n"
    "print('\\n'.join(lines[-40:]))\n"
)
print(d.Dswhub().run_python(code, timeout=90))

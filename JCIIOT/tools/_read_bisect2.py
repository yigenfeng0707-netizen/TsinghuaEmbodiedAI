import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python('print(open("/mnt/workspace/_bisect2.log").read()[-2500:])', timeout=60))

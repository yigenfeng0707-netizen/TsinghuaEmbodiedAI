import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python("print(open('/mnt/workspace/_bisect6.log').read()[-2800:])", timeout=60))

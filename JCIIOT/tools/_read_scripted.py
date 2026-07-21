import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
print(d.Dswhub().run_python("print(open('/mnt/workspace/_scripted_grasp_test.log').read()[-3000:])", timeout=30))

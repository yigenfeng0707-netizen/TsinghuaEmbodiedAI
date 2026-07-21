import sys, time
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
time.sleep(120)
print(d.Dswhub().run_python("import os\nprint(open('/mnt/workspace/_obscmp.log').read()[-2000:])", timeout=60))

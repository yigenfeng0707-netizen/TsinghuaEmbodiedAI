import sys, time
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
time.sleep(120)
print(d.Dswhub().run_python("import os\nprint(open('/mnt/workspace/_polact.log').read()[-1500:])", timeout=60))

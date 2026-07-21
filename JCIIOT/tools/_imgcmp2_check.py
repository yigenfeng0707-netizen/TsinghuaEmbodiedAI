import sys, time
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
time.sleep(90)
print(d.Dswhub().run_python("import os\nprint(open('/mnt/workspace/_imgcmp2.log').read()[-1200:])", timeout=60))

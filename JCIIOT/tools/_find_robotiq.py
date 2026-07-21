import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print(c.run_python(
"import glob\n"
"for pat in ['**/*Robotiq140*', '**/*robotiq*']:\n"
"    for h in glob.glob('/mnt/workspace/JCIIOT_repo/JCIIOT/'+pat, recursive=True)[:8]:\n"
"        print(h)\n", timeout=30))

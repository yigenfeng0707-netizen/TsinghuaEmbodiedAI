import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print(c.run_python(
"import glob\n"
"for pat in ['/mnt/workspace/JCIIOT_repo/JCIIOT/**/scor*.py','/mnt/workspace/JCIIOT_repo/JCIIOT/**/*grasp_success*','/mnt/workspace/JCIIOT_repo/JCIIOT/**/*gate*']:\n"
"    for h in glob.glob(pat, recursive=True)[:8]:\n"
"        print(h)\n", timeout=30))

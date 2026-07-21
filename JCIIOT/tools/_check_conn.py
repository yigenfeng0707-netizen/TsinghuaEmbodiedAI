import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

c = d.Dswhub()
print("contents root:", [x["name"] for x in c.contents("")["content"][:12]])

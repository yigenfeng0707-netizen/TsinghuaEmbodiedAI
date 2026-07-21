import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
txt = open("/mnt/workspace/_smoke.log").read()
idx = txt.find("mj_fullM(): incompatible")
print(txt[idx: idx+800])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))

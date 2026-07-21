import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os
p = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/controllers/parts/controller.py"
t = open(p).read()
i = t.find("mj_fullM")
print(t[max(0,i-500): i+400])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))

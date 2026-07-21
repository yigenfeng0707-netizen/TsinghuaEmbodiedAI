import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, sys
# set software GL backend BEFORE importing mujoco
os.environ["MUJOCO_GL"] = "mujoco"
for k in list(sys.modules):
    if k == "mujoco" or k.startswith("mujoco."):
        del sys.modules[k]
import mujoco
print("mj", mujoco.__version__, "Renderer?", hasattr(mujoco, "Renderer"))
import numpy as np
m = mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type=\"sphere\" size=\"0.1\"/></worldbody></mujoco>")
d = mujoco.MjData(m)
r = mujoco.Renderer(m, 64, 64); r.update_scene(d); img = r.render()
print("SW RENDER OK", img.shape)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=90))

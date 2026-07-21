import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, subprocess
os.environ.pop("MUJOCO_GL", None)
# install glfw (needed by robosuite viewer) without touching torch
print(subprocess.run("pip install glfw --no-deps -q 2>&1 | tail -2", shell=True, capture_output=True, text=True).stdout[-300:])

import numpy as np, mujoco
print("mj", mujoco.__version__, "Renderer?", hasattr(mujoco, "Renderer"))
m = mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type=\"sphere\" size=\"0.1\"/></worldbody></mujoco>")
d = mujoco.MjData(m)
r = mujoco.Renderer(m, 64, 64)
r.update_scene(d)
img = r.render()
print("SW RENDER OK shape", img.shape)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=180))

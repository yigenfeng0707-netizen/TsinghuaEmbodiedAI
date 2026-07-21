import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os
os.environ.pop("MUJOCO_GL", None)
import mujoco
print("mj version", mujoco.__version__)
print("has Renderer attr:", hasattr(mujoco, "Renderer"))
import mujoco.viewer as v
print("viewer ok")
# try the documented 3.x renderer
import numpy as np
xml = "<mujoco><worldbody><geom type=\"sphere\" size=\"0.1\"/></worldbody></mujoco>"
m = mujoco.MjModel.from_xml_string(xml)
d = mujoco.MjData(m)
try:
    r = mujoco.Renderer(m, 64, 64)
    r.update_scene(d); r.render()
    print("Renderer OK, frame shape", r.render().shape)
except Exception as e:
    print("Renderer ERR:", repr(e)[:200])
# glfw availability
try:
    import glfw; print("glfw OK", glfw.__version__)
except Exception as e:
    print("glfw MISSING:", e)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=120))

import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os
os.environ.pop("MUJOCO_GL", None)
import numpy as np, mujoco
print("mj", mujoco.__version__)
# canonical renderer import for 3.x
try:
    from mujoco.rendering import Renderer as R
    print("mujoco.rendering.Renderer OK")
except Exception as e:
    print("rendering import ERR", repr(e)[:120])
m = mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type=\"sphere\" size=\"0.1\"/></worldbody></mujoco>")
d = mujoco.MjData(m)
# try software backend explicitly
for gl in ["mujoco", "osmesa", "egl"]:
    os.environ["MUJOCO_GL"] = gl
    try:
        r = R(m, 64, 64); r.update_scene(d); img = r.render()
        print(f"GL={gl} RENDER OK shape {img.shape}")
        break
    except Exception as e:
        print(f"GL={gl} ERR:", repr(e)[:140])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=120))

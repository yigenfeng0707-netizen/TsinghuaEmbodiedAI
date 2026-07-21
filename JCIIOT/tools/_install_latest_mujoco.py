import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, subprocess, glob
os.environ.pop("MUJOCO_GL", None)
# install latest mujoco (supports MUJOCO_GL=mujoco software backend + top-level Renderer)
rc = subprocess.run("pip install mujoco --no-deps --force-reinstall 2>&1 | tail -5", shell=True, capture_output=True, text=True)
print("install rc", rc.returncode, rc.stdout[-400:])
import mujoco
print("mj", mujoco.__version__, "Renderer?", hasattr(mujoco, "Renderer"))
import numpy as np
m = mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type=\"sphere\" size=\"0.1\"/></worldbody></mujoco>")
d = mujoco.MjData(m)
os.environ["MUJOCO_GL"] = "mujoco"
r = mujoco.Renderer(m, 64, 64); r.update_scene(d); img = r.render()
print("SW RENDER OK", img.shape)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=240))

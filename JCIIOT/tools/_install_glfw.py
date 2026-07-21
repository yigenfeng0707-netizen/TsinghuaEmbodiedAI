import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, subprocess
os.environ.pop("MUJOCO_GL", None)
rc = subprocess.run("pip install glfw --no-deps 2>&1 | tail -3", shell=True, capture_output=True, text=True)
print("glfw install:", rc.returncode, rc.stdout[-200:])
# glfw needs libGL/libX11; check
rc = subprocess.run("ldconfig -p | grep -iE 'libglfw|libX11' | head", shell=True, capture_output=True, text=True)
print("libs:", rc.stdout.strip())
import mujoco
print("mj", mujoco.__version__, "Renderer?", hasattr(mujoco, "Renderer"))
if hasattr(mujoco, "Renderer"):
    import numpy as np
    m = mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type=\"sphere\" size=\"0.1\"/></worldbody></mujoco>")
    d = mujoco.MjData(m)
    os.environ["MUJOCO_GL"] = "mujoco"
    r = mujoco.Renderer(m, 64, 64); r.update_scene(d); img = r.render()
    print("SW RENDER OK", img.shape)
'''
c = d.Dswhub()
print(c.run_python(code, timeout=150))

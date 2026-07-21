import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, mujoco
os.environ.pop("MUJOCO_GL", None)
print("mj", mujoco.__version__)
import mujoco.rendering as mr
print("rendering attrs:", [a for a in dir(mr) if not a.startswith("_")])
print("mujoco top Renderer?", hasattr(mujoco, "Renderer"))
# viewer Renderer
try:
    from mujoco.viewer import Renderer as VR
    print("mujoco.viewer.Renderer OK")
except Exception as e:
    print("viewer.Renderer ERR", repr(e)[:120])
# old-style MjRenderContext
print("MjRenderContext?", hasattr(mujoco, "MjRenderContext"))
'''
c = d.Dswhub()
print(c.run_python(code, timeout=90))

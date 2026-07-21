import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import os, sys, subprocess
# run in a subprocess with its own timeout so it can't hang the kernel
script = '''
import os, numpy as np
os.environ["MUJOCO_GL"]="osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
import mujoco
print("mj", mujoco.__version__, "Renderer?", hasattr(mujoco,"Renderer"), flush=True)
m=mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type=\\"sphere\\" size=\\"0.1\\"/></worldbody></mujoco>")
d=mujoco.MjData(m)
r=mujoco.Renderer(m,64,64); r.update_scene(d); img=r.render()
print("OSMESA RENDER OK", img.shape, flush=True)
'''
r = subprocess.run(["python","-c",script], capture_output=True, text=True, timeout=80, env={**os.environ, "MUJOCO_GL":"osmesa"})
print("RC", r.returncode)
print("OUT:", r.stdout[-600:])
print("ERR:", r.stderr[-600:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=120))

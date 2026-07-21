import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import os
os.environ["MUJOCO_GL"] = "osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
import numpy as np, torch, mujoco
print("torch", torch.__version__, "cuda/rocm", torch.cuda.is_available())
print("mujoco", mujoco.__version__, "Renderer?", hasattr(mujoco, "Renderer"))
import robosuite
print("robosuite", robosuite.__version__)
import robomimic
print("robomimic", getattr(robomimic, "__version__", "ok"))
# load a tiny mujoco model via robosuite renderer path to confirm offscreen works
import mujoco
m = mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type=\\"sphere\\" size=\\"0.1\\"/></worldbody></mujoco>")
d = mujoco.MjData(m)
r = mujoco.Renderer(m, 64, 64); r.update_scene(d); img = r.render()
print("render shape", img.shape)
print("ALL IMPORTS OK")
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_verify_stack.py", json=payload, timeout=30)

code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa"}
r = subprocess.run(["python", "/mnt/workspace/_verify_stack.py"], capture_output=True, text=True, timeout=120, env=env)
print("RC", r.returncode)
print(r.stdout[-900:])
print("ERR:", r.stderr[-500:])
'''
print(c.run_python(code, timeout=150))

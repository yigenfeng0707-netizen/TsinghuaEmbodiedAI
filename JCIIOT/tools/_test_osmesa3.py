import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import os, numpy as np
os.environ["MUJOCO_GL"] = "osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
import mujoco
print("mj", mujoco.__version__, "Renderer?", hasattr(mujoco, "Renderer"), flush=True)
m = mujoco.MjModel.from_xml_string("<mujoco><worldbody><geom type=\\"sphere\\" size=\\"0.1\\"/></worldbody></mujoco>")
d = mujoco.MjData(m)
r = mujoco.Renderer(m, 64, 64); r.update_scene(d); img = r.render()
print("OSMESA RENDER OK", img.shape, flush=True)
'''

# upload inner script via contents API
c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
rr = c.s.put(d.BASE + "/api/contents/_osmesa_test.py", json=payload, timeout=30)
print("upload", rr.status_code)

code = r'''
import subprocess, os
r = subprocess.run(["python", "/mnt/workspace/_osmesa_test.py"], capture_output=True, text=True, timeout=90, env={**os.environ, "MUJOCO_GL": "osmesa"})
print("RC", r.returncode)
print("OUT:", r.stdout[-700:])
print("ERR:", r.stderr[-700:])
'''
print(c.run_python(code, timeout=120))

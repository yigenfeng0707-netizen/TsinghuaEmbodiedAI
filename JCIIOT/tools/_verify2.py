import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import os
os.environ["MUJOCO_GL"] = "osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
import robomimic
print("robomimic", getattr(robomimic, "__version__", "ok"), "OK")
from robomimic.envs import base as rb
print("robomimic.envs OK")
import robosuite
print("robosuite", robosuite.__version__)
# locate the demo collection script
import glob, os
base="/mnt/workspace/JCIIOT_repo/JCIIOT"
hits=glob.glob(os.path.join(base,"robosuite/robosuite/environments/factory_sorting/*collect*.py"))
print("collect scripts:", [os.path.basename(h) for h in hits])
# confirm robomimic algo BC trainable import
from robomimic.algo import algo_factory
print("algo_factory OK")
print("ALL GOOD")
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_verify2.py", json=payload, timeout=30)

code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa"}
r = subprocess.run(["python", "/mnt/workspace/_verify2.py"], capture_output=True, text=True, timeout=120, env=env)
print("RC", r.returncode)
print(r.stdout[-1000:])
print("ERR:", r.stderr[-500:])
'''
print(c.run_python(code, timeout=150))

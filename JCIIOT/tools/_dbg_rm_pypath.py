import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa",
       "PYTHONPATH": "/mnt/workspace/JCIIOT_repo/JCIIOT:" + os.environ.get("PYTHONPATH","")}
r = subprocess.run("python -c \"import robomimic; print('robomimic', getattr(robomimic,'__version__','ok'),'OK')\" 2>&1", shell=True, capture_output=True, text=True, timeout=60, env=env)
print("WITH PYTHONPATH RC", r.returncode)
print(r.stdout[-400:]); print("ERR", r.stderr[-600:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=120))

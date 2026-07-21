import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa"}
r = subprocess.run("cd /mnt/workspace/JCIIOT_repo/JCIIOT && pip install -e ./robomimic --no-deps 2>&1 | tail -25", shell=True, capture_output=True, text=True, timeout=200, env=env)
print("RC", r.returncode)
print(r.stdout[-1500:])
print("ERR:", r.stderr[-600:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=240))

import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa"}
# uninstall broken editable
subprocess.run("pip uninstall -y robomimic 2>&1 | tail -2", shell=True, capture_output=True, text=True, env=env)
# reinstall with legacy compat editable mode
r = subprocess.run("cd /mnt/workspace/JCIIOT_repo/JCIIOT && pip install -e ./robomimic --no-deps --config-settings editable_mode=compat 2>&1 | tail -8", shell=True, capture_output=True, text=True, timeout=200, env=env)
print("install RC", r.returncode, r.stdout[-500:])
# verify WITHOUT pypath
r2 = subprocess.run("python -c \"import robomimic; print('robomimic OK', getattr(robomimic,'__version__','?'))\" 2>&1", shell=True, capture_output=True, text=True, timeout=60, env={**env, "PYTHONPATH":""})
print("verify RC", r2.returncode, r2.stdout[-300:], r2.stderr[-300:])
# also robosuite editable compat
subprocess.run("pip uninstall -y robosuite 2>&1 | tail -1", shell=True, capture_output=True, text=True, env=env)
r3 = subprocess.run("cd /mnt/workspace/JCIIOT_repo/JCIIOT && pip install -e ./robosuite --no-deps --config-settings editable_mode=compat 2>&1 | tail -6", shell=True, capture_output=True, text=True, timeout=200, env=env)
print("robosuite install RC", r3.returncode, r3.stdout[-300:])
r4 = subprocess.run("python -c \"import robosuite,robomimic; print('BOTH OK', robosuite.__version__)\" 2>&1", shell=True, capture_output=True, text=True, timeout=60, env={**env, "PYTHONPATH":""})
print("both RC", r4.returncode, r4.stdout[-200:], r4.stderr[-200:])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=400))

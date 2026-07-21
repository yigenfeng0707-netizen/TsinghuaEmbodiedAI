import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import os, subprocess
os.environ["MUJOCO_GL"] = "osmesa"
# editable install robomimic (no deps to keep torch/rocm stack)
print(subprocess.run("cd /mnt/workspace/JCIIOT_repo/JCIIOT && pip install -e ./robomimic --no-deps 2>&1 | tail -5", shell=True, capture_output=True, text=True).stdout[-400:])
import robomimic
print("robomimic", getattr(robomimic, "__version__", "ok"), "OK")
# also ensure robosuite editable present
print(subprocess.run("cd /mnt/workspace/JCIIOT_repo/JCIIOT && pip install -e ./robosuite --no-deps 2>&1 | tail -3", shell=True, capture_output=True, text=True).stdout[-200:])
# persist MUJOCO_GL in bashrc for future shell/run_all sessions
subprocess.run("grep -q MUJOCO_GL=osmesa ~/.bashrc || echo 'export MUJOCO_GL=osmesa' >> ~/.bashrc", shell=True)
print("bashrc updated")
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_install_robomimic.py", json=payload, timeout=30)

code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa"}
r = subprocess.run(["python", "/mnt/workspace/_install_robomimic.py"], capture_output=True, text=True, timeout=180, env=env)
print("RC", r.returncode)
print(r.stdout[-900:])
print("ERR:", r.stderr[-400:])
'''
print(c.run_python(code, timeout=200))

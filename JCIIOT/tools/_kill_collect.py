import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''import os, subprocess, signal
os.environ["MUJOCO_GL"] = "osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
# kill existing collect
subprocess.run("pkill -f load_factory_sorting_1_3fo3erfhisem_collect", shell=True)
print("killed old collect")
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_kill_collect.py", json=payload, timeout=30)
code = r'''import subprocess, os
r = subprocess.run(["python", "/mnt/workspace/_kill_collect.py"], capture_output=True, text=True, timeout=60, env={**os.environ, "MUJOCO_GL":"osmesa"})
print(r.stdout[-300:], r.stderr[-200:])
# confirm dead
r2 = subprocess.run("pgrep -f load_factory_sorting_1_3fo3erfhisem_collect | head", shell=True, capture_output=True, text=True)
print("remaining pids:", r2.stdout.strip() or "none")
'''
print(c.run_python(code, timeout=90))
